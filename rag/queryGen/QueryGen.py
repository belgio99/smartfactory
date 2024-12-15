from dateutil.relativedelta import relativedelta
from itertools import product
from dotenv import load_dotenv
import os
from rdflib import Graph
# Load environment variables
load_dotenv()
from datetime import datetime, timedelta
# the class is accessible only following the route of classified label == "kpi_calc" or label =="predictions"
class QueryGenerator:
    ERROR_NO_KPIS = 2
    ERROR_ALL_KPIS = 1
    def __init__(self, llm):
        self.llm=llm

    def _string_to_array(self,string ,type):
        # there are specific cases where llm may return kpis or machines which does not belong to the KB
        # Example: Assembly machine 6 even tough is not in KB may be returned because 
        # llm think it may be a typo but can't disambiguate between the Assembly machines actually in the KB
        # this function doesn't returns the kpis/machines not in kb
        string = string.strip("[]").split(", ")
        array = []
        for x in string:
            x=x.strip("'")
            if (type == "machines" and (x in self.machine_res)) or (type == "kpis" and (x in self.kpi_res)) or x == "ALL" or x == "NULL":
                array.append(x)
        return array
    
    def _check_absolute_time_window(self,dates:datetime,label):
        # the time window is 'dates[0] -> dates[1]', check if dates[0] < dates[1] and for some formatting error
        try: 
            start = datetime.strptime(dates[0], "%Y-%m-%d")
            end = datetime.strptime(dates[1], "%Y-%m-%d")
        except:
            return False
        if (end -start).days < 0:
            return False
        # there are two delta due to a the following user case:
        # TODAY is somewhere in the middle of april and the input is "predict/calculate X for the month of April 2024"
        # rag has to calculate for only a fraction of the month
        delta_p = (end - self.TODAY).days
        delta_k = (start - self.TODAY).days
        if (delta_p > 0 and label == "predictions") or (delta_k < 0 and label == "kpi_calc"):
            return True
        # time window not consistent with label or attempt to calculate/predict for Today
        return False

            
    def _kb_update(self):
        temp = datetime.now()
        self.TODAY = datetime(year=temp.year,month=temp.month,day=temp.day)
        kpi_query= """
        PREFIX ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>
        SELECT ?id WHERE {
        ?kpi rdf:type ?type.
        FILTER (?type IN (ontology:ProductionKPI_Production, ontology:EnergyKPI_Consumption, ontology:EnergyKPI_Cost, ontology:MachineUsageKPI, ontology:ProductionKPI_Quality, ontology:CustomKPItmp)).
        ?kpi ontology:id ?id .
        }
        """
        machine_query="""
        PREFIX ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>
        SELECT ?id WHERE {
        ?machine rdf:type ?type
        FILTER (?type IN (ontology:AssemblyMachine, ontology:LargeCapacityCuttingMachine, ontology:LaserCutter, ontology:LaserWeldingMachine, ontology:LowCapacityCuttingMachine, ontology:MediumCapacityCuttingMachine, ontology:RivetingMachine, ontology:TestingMachine)).
        ?machine ontology:id ?id.
        }
        """
        graph = Graph()
        graph.parse(os.environ['KB_FILE_PATH'] + os.environ['KB_FILE_NAME'], format="xml")
        res = graph.query(kpi_query)
        self.kpi_res = []
        for row in res:
            self.kpi_res.append(str(row["id"]))
        res = graph.query(machine_query)
        self.machine_res = []
        for row in res:
            self.machine_res.append(str(row["id"]))

    def _last_next_days(self,data,time,days):
        if time == "last":
            start = data - timedelta(days=days)
            end = data - timedelta(days= 1)
            return start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d')
        # time == next    
        elif time == "next": 
            return days
        else: 
            return "INVALID DATE"
        
    def _last_next_weeks(self,data,time,weeks):
        if time == "last":
            # Calcola il giorno della settimana (0=Lunedì, 6=Domenica)
            start = data - timedelta(days=(7 * weeks) +data.weekday())
            end = data - timedelta(days= 1 +data.weekday())
            return start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d')
        # time == next    
        elif time == "next":
            # 7 - data.weekday() -> monday of the following week
            return (7 - data.weekday()) + 7 * weeks - 1
        else: 
            return "INVALID DATE"
        
    def _last_next_months(self,data,time,months):
        first_of_the_current_month= data - relativedelta(days= data.day-1)
        if time == "last":
            end_of_the_month = first_of_the_current_month - relativedelta(days=1)
            first_of_the_month = first_of_the_current_month - relativedelta(months= months)
            return first_of_the_month.strftime('%Y-%m-%d') , end_of_the_month.strftime('%Y-%m-%d')
        # time == next    
        elif time == "next":
            first_of_the_month = first_of_the_current_month + relativedelta(months= 1)
            end_of_the_month = first_of_the_month + relativedelta(months= months) - relativedelta(days = 1)
            return (end_of_the_month - data).days
        else: 
            return "INVALID DATE"   
        
    
    # input: a time window outputted from the llm
    # return: a time window in the required format
    def _date_parser(self,date,label):
        if date == "NULL": 
            # date not provided from the user => default action
            if label == "kpi_calc":
                return self._last_next_days(self.TODAY,"last",30)
            else:
                return self._last_next_days(self.TODAY,"next",30)
        # absolute time window
        if "->" in date:
            temp=date.split(" -> ")
            if not(self._check_absolute_time_window(temp,label)):
                return "INVALID DATE"
            delta= (datetime.strptime(temp[1], "%Y-%m-%d")-self.TODAY).days
            if label == "predictions":
                return delta
            if delta >= 0:
                # the time window is only partially calculable because TODAY is within it
                return temp[0], (self.TODAY- relativedelta(days=1)).strftime('%Y-%m-%d')
            return temp[0],temp[1]
        # relative time window
        if "<" in date:
            # date format: <last/next, X, days/weeks/months>
            temp=date.strip("<>").split(", ")
            temp[1]=int(temp[1])
            if (temp[0] == "last" and label != "kpi_calc") or (temp[0] == "next" and label != "predictions") or temp[1] == 0:
                return "INVALID DATE"
            if temp[2] == "days":
                return self._last_next_days(self.TODAY,temp[0],temp[1])
            elif temp[2] == "weeks":
                return self._last_next_weeks(self.TODAY,temp[0],temp[1])
            elif temp[2] == "months":
                return self._last_next_months(self.TODAY,temp[0],temp[1])
        return "INVALID DATE"

    # input: 
    #   data: output of llm invocation, in the format: OUTPUT: (query1), (query2), (query3)
    #   label: classification label for the user input,
    # output: json formatted string which will be sended to other modules, if all data is not valid the outbut will be {"value": []}
    def _json_parser(self, data, label):
        json_out= []
        all_kpis = 0
        data = data.replace("OUTPUT: ","")
        data= data.strip("()").split("), (")
        # for each elem in data, a dictionary (json obj) is created
        for elem in data:
            obj={}
            # it is necessary to include ']' in the split because otherwise would also be included in the splitting, each element of the arrays
            elem = elem.split("], ")
            kpis=elem[1]+"]"
            kpis = self._string_to_array(kpis,"kpis")
            # a request is invalid if it misses the kpi field or if the user query mentions 'all' kpis to be calculate/predicted
            # return also a log of the fact that the user cant' ask for all kpis
            if kpis == ["ALL"]:
                all_kpis = self.ERROR_ALL_KPIS
                continue
            if kpis == ["NULL"]:
                all_kpis= self.ERROR_NO_KPIS
                continue
            date = self._date_parser(elem[2],label)
            # if there is no valid time window, the related json obj is not built
            if date == "INVALID DATE":
                continue
            # kpi-engine get a time window with variable starting point while predictor starts always from the day next to the current one
            if label == "kpi_calc":
                obj["Date_Start"] = date[0]
                obj["Date_Finish"] = date[1]
            else:
                # predictions
                obj["Date_prediction"] = date

            machines=elem[0]+"]"
            # transform the string containing the array of machines in an array of string
            machines = self._string_to_array(machines,"machines")
            # machines == ["NULL/ALL"] => no usage of the Machine_Name key
            if  machines != ["NULL"] and machines != ["ALL"]:                
                for machine, kpi in product(machines,kpis):
                    new_dict=obj.copy()
                    new_dict["Machine_Name"]=machine
                    new_dict["KPI_Name"] = kpi
                    json_out.append(new_dict)
            else:
                # only kpis names are added to json obj
                for kpi in kpis:
                    new_dict=obj.copy()
                    new_dict["KPI_Name"] = kpi
                    json_out.append(new_dict)

        if label == "predictions" :
            json_out={"value":json_out}
  
        return json_out,all_kpis

    def query_generation(self,input= "predict idle time max, cost wrking sum and good cycles min for last week for all the medium capacity cutting machine, predict the same kpis for Laser welding machines 2 for today. calculate the cnsumption_min for next 4 month and for Laser cutter the offline time sum for last 23 day. "
, label="kpi_calc"):
        
        self._kb_update()
        YESTERDAY = f"{(self.TODAY-relativedelta(days=1)).strftime('%Y-%m-%d')} -> {(self.TODAY-relativedelta(days=1)).strftime('%Y-%m-%d')}"
        query= f"""
            USER QUERY: {input}

            INSTRUCTIONS: 
            Extract information from the USER QUERY based on the following rules and output it in the EXAMPLE OUTPUT specified format.
            All dates in the USER QUERY are in the format DD/MM/YYYY. When providing your OUTPUT, always convert all dates to the format YYYY-MM-DD. If a date range is given, maintain the range format (e.g., "01/12/2024 -> 10/12/2024" should become "2024-12-01 -> 2024-12-10").

            LIST_1 (list of machines): '{self.machine_res}'
            LIST_2 (list of kpis): '{self.kpi_res}'

            RULES:
            1. Match IDs:
                -Look for any terms in the query that match IDs from LIST_1 or LIST_2.
                -If a match contains a machine type without a specific number, return all machines of that type. Example: 'Testing Machine' -> ['Testing Machine 1', 'Testing Machine 2', 'Testing Machine 3'].
                -If no IDs from LIST_2 are associated with the matched KPIs, return ['NULL'] as [matched LIST_2 IDs].
                -If no IDs from LIST_1 are associated with the matched machines, return ['NULL'] as [matched LIST_1 IDs].
                -If 'all' IDs from LIST_2 are associated with the matched KPIs, return ['ALL'] as [matched LIST_2 IDs]. Example: 'predict all kpis for ...' -> ['ALL']
                -If 'all' IDs from LIST_1 are associated with the matched machines, return ['ALL'] as [matched LIST_1 IDs]. Example: 'calculate for all machines ...' -> ['ALL']
            2. Determine Time Window:
                -if there is a time window described by exact dates, use them, otherwise return the expression which individuates the time window: 'last/next X days/weeks/months' using the format <last/next, X, days/weeks/months>
                -If no time window is specified, use NULL.
                -if there is a reference to an exact month and a year, return the time windows starting from the first of that month and ending to the last day of that month.
                -Yesterday must be returned as {YESTERDAY}, today as {(self.TODAY).strftime('%Y-%m-%d')} -> {(self.TODAY).strftime('%Y-%m-%d')} and tomorrow as {(self.TODAY+relativedelta(days=1)).strftime('%Y-%m-%d')} -> {(self.TODAY+relativedelta(days=1)).strftime('%Y-%m-%d')}.
                -Allow for minor spelling or formatting mistakes in the matched expressions and correct them as done in the examples below.
            3. Handle Errors:
                -Allow for minor spelling or formatting mistakes in the input.
                -If there is ambiguity matching a kpi, you can match USER QUERY with the one in LIST_2 which ends with '_avg'"""
        # There is a different output format between report and (kpi_calc and predictions) use cases so there will be a different prompt
        # kpi_cal and predictions prompt
        if label == "kpi_calc" or label == "predictions":
            query+=f"""
            4. Output Format:
                -For each unique combination of machine IDs and KPIs, return a tuple in this format: ([matched LIST_1 IDs], [matched LIST_2 IDs], time window), time window in the format 'YYYY-MM-DD -> YYYY-MM-DD'.
                
            NOTES:
            -Ensure output matches the one of the EXAMPLES below exactly, I need only the OUTPUT section.

            EXAMPLES:
            '
            LIST_1: [cost_idle_avg, cost_idle_std, offline_time_med, offline_time_max, working_time_min, working_time_sum, working_time_avg]
            LIST_2: [Assembly Machine 1, Low Capacity Cutting Machine 1, Assembly Machine 2]

            INPUT: Calculate the kpi cost_idle arg and cost idle std for the assembly machine 1 and Low capacity cutting machine for the past 5 day, calculate offlinetime med for Assembly machine 2 for the last two months and cost_idle_avg for Assembly machine. How much do the Assembly machine 2 has worked the last three days? Can you calculate all kpis for 20/11/2024 -> 18/11/2024 for Low Capacity Cutting Machine 1?
            OUTPUT: (['Assembly Machine 1', 'Low Capacity Cutting Machine 1'], ['cost_idle_avg', 'cost_idle_std'], <last, 5, days>), (['Assembly Machine 2'], ['offline_time_med'], <last, 2, months>), (['Assembly Machine 1', 'Assembly Machine 2'], ['cost_idle_avg'], NULL), (['Assembly Machine 2'], ['working_time_sum'], <last, 3, days>), (['Low Capacity Cutting Machine 1'], ['ALL'], 2024-11-20 -> 2024-11-18)

            INPUT: Calculate using data from the last 2 weeks the standard deviation for cost_idle of Low capacity cutting machine 1 and Assemby Machine 2. Calculate for the same machines also the offline time median using data from the past month. Calculate the highest offline time for low capacity cutting machine 1?
            OUTPUT: (['Low Capacity Cutting Machine 1', 'Assembly Machine 2'], ['cost_idle_std'], <last, 2, weeks>), (['Low Capacity Cutting Machine 1', 'Assembly Machine 2'], ['offline_time_med'], <last, 1, months>), (['Low Capacity Cutting Machine 1'], ['offline_time_max'], NULL)

            INPUT: Calculate the offline time median about laste 3 weeks. Can you calculate the working time for Assembly machine 1 based on yesterday data, the same kpi dor Assembly machine 2 based on data from 03/05/2024 -> 07/06/2024. What is the day low capacity cutting machine 1 had the lowest working time last 2 months.
            OUTPUT: (['NULL'], ['offline_time_med'], <last, 3, weeks>), (['Assembly Machine 1'], ['working_time_avg'], {YESTERDAY}), (['Assembly Machine 2'], ['working_time_avg'], 2024-05-03 ->2024-06-07), (['Low Capacity Cutting Machine 1'], ['working_time_min'], <last, 2, months>)

            INPUT: Predict working time min and the average for Assembly machine for {(self.TODAY + relativedelta(days=5)).strftime('%d/%m/%Y')} -> {(self.TODAY + relativedelta(days=13)).strftime('%d/%m/%Y')} and the same kpis for all machines. What will be the the total amount of working time for low capacity cutting machine 1 and assembly machine 1 for next 5 weeks.
            OUTPUT: (['Assembly Machine 1', 'Assembly Machine 2'], ['working_time_min','working_time_avg'], {(self.TODAY + relativedelta(days=5)).strftime('%Y-%m-%d')} -> {(self.TODAY + relativedelta(days=13)).strftime('%Y-%m-%d')}), (['ALL'], ['working_time_min','working_time_avg'], NULL), (['Low Capacity Cutting Machine 1', 'Assembly Machine 1'], ['working_time_sum'], <next, 5, weeks>)

            INPUT: Can you predict for next 2 days for Assembly machine 1? predict for all the assembly machine the cost idle average and the sum of working time for the next 3 weeks and for low capacity cutting machne the cost_idle_std for March 2025. predict also for Assembly machine 1 the cost_idle for the next two days.
            OUTPUT: (['Assembly Machine 1'], ['NULL'], <next, 2, days>), (['Assembly Machine 1', 'Assembly Machine 2'], ['cost_idle_avg', 'working_time_sum'], <next, 3, weeks>), (['Low Capacity Cutting Machine 1'], ['cost_idle_std'], 2025-03-01 -> 2025-03-31), (['Assembly Machine 1'], ['cost_idle_avg'], <next, 2, days>)
            '
            """
        else:
            query+=f"""
            4. Output Format:
                -For each unique combination of machine IDs and KPIs, return a tuple in this format: ([matched LIST_1 IDs], [matched LIST_2 IDs], time window), time window in the format 'YYYY-MM-DD -> YYYY-MM-DD'.
                
            NOTES:
            -Ensure output matches the one of the EXAMPLES below exactly, I need only the OUTPUT section.

            EXAMPLES:
            '
            LIST_1: [cost_idle_avg, cost_idle_std, offline_time_med, offline_time_max, working_time_min, working_time_sum, working_time_avg]
            LIST_2: [Assembly Machine 1, Low Capacity Cutting Machine 1, Assembly Machine 2]

            INPUT: Calculate the kpi cost_idle arg and cost idle std for the assembly machine 1 and Low capacity cutting machine for the past 5 day, calculate offlinetime med for Assembly machine 2 for the last two months and cost_idle_avg for Assembly machine. How much do the Assembly machine 2 has worked the last three days? Can you calculate all kpis for 20/11/2024 -> 18/11/2024 for Low Capacity Cutting Machine 1?
            OUTPUT: (['Assembly Machine 1', 'Low Capacity Cutting Machine 1'], ['cost_idle_avg', 'cost_idle_std'], <last, 5, days>), (['Assembly Machine 2'], ['offline_time_med'], <last, 2, months>), (['Assembly Machine 1', 'Assembly Machine 2'], ['cost_idle_avg'], NULL), (['Assembly Machine 2'], ['working_time_sum'], <last, 3, days>), (['Low Capacity Cutting Machine 1'], ['ALL'], 2024-11-20 -> 2024-11-18)

            INPUT: Calculate using data from the last 2 weeks the standard deviation for cost_idle of Low capacity cutting machine 1 and Assemby Machine 2. Calculate for the same machines also the offline time median using data from the past month. Calculate the highest offline time for low capacity cutting machine 1?
            OUTPUT: (['Low Capacity Cutting Machine 1', 'Assembly Machine 2'], ['cost_idle_std'], <last, 2, weeks>), (['Low Capacity Cutting Machine 1', 'Assembly Machine 2'], ['offline_time_med'], <last, 1, months>), (['Low Capacity Cutting Machine 1'], ['offline_time_max'], NULL)

            INPUT: Calculate the offline time median about laste 3 weeks. Can you calculate the working time for Assembly machine 1 based on yesterday data, the same kpi dor Assembly machine 2 based on data from 03/05/2024 -> 07/06/2024. What is the day low capacity cutting machine 1 had the lowest working time last 2 months.
            OUTPUT: (['NULL'], ['offline_time_med'], <last, 3, weeks>), (['Assembly Machine 1'], ['working_time_avg'], {YESTERDAY}), (['Assembly Machine 2'], ['working_time_avg'], 2024-05-03 ->2024-06-07), (['Low Capacity Cutting Machine 1'], ['working_time_min'], <last, 2, months>)

            INPUT: Predict working time min and the average for Assembly machine for {(self.TODAY + relativedelta(days=5)).strftime('%d/%m/%Y')} -> {(self.TODAY + relativedelta(days=13)).strftime('%d/%m/%Y')} and the same kpis for all machines. What will be the the total amount of working time for low capacity cutting machine 1 and assembly machine 1 for next 5 weeks.
            OUTPUT: (['Assembly Machine 1', 'Assembly Machine 2'], ['working_time_min','working_time_avg'], {(self.TODAY + relativedelta(days=5)).strftime('%Y-%m-%d')} -> {(self.TODAY + relativedelta(days=13)).strftime('%Y-%m-%d')}), (['ALL'], ['working_time_min','working_time_avg'], NULL), (['Low Capacity Cutting Machine 1', 'Assembly Machine 1'], ['working_time_sum'], <next, 5, weeks>)

            INPUT: Can you predict for next 2 days for Assembly machine 1? predict for all the assembly machine the cost idle average and the sum of working time for the next 3 weeks and for low capacity cutting machne the cost_idle_std for March 2025. predict also for Assembly machine 1 the cost_idle for the next two days.
            OUTPUT: (['Assembly Machine 1'], ['NULL'], <next, 2, days>), (['Assembly Machine 1', 'Assembly Machine 2'], ['cost_idle_avg', 'working_time_sum'], <next, 3, weeks>), (['Low Capacity Cutting Machine 1'], ['cost_idle_std'], 2025-03-01 -> 2025-03-31), (['Assembly Machine 1'], ['cost_idle_avg'], <next, 2, days>)
            '
            """

        data = self.llm.invoke(query)
        data = data.content.strip("\n")
        print(data)
        json_obj = self._json_parser(data,label)
        
        print("\n")
        print(json_obj)
        

        return json_obj
    