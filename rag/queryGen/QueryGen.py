from dateutil.relativedelta import relativedelta
import json
from itertools import product
import ast
from dotenv import load_dotenv
import os
from pathlib import Path
from rdflib import Graph
# Load environment variables
load_dotenv()
from datetime import datetime, timedelta

class QueryGenerator:

    def __init__(self, llm):
        self.llm=llm


    def _kb_update(self):
        self.TODAY = datetime.now()
        kpi_query= """
        PREFIX ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>
        SELECT ?id WHERE {
        ?kpi rdf:type ?type.
        FILTER (?type IN (ontology:ProductionKPI_Production, ontology:AtomicIdleTime, ontology:AtomicGoodCycles, ontology:EnergyKPI_Cost, ontology:AtomicCycles, ontology:MachineUsageKPI, ontology:AtomicOfflineTime, ontology:ProductionKPI_Quality, ontology:EnergyKPI_Consumption, ontology:AtomicWorkingTime, ontology:AtomicPower, ontology:AtomicCostWorking, ontology:AtomicCostIdle, ontology:AtomicCost, ontology:AtomicConsumptionWorking, ontology:AtomicAvgCycleTime, ontology:AtomicConsumption, ontology:AtomicBadCycles, ontology:AtomicConsumptionIdle, ontology:CustomKPItmp)).
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
        graph_dir=Path(os.path.dirname(os.path.abspath(__file__))+"/../docs/sa_ontology.rdf").as_uri()
        graph = Graph()
        graph.parse(graph_dir, format="xml")
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
        # time == next    
        elif time == "next": 
            start = data + timedelta(days=1)
            end = start + timedelta(days = days)
        else: 
            return "INVALID DATE"
        return start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d')

    def _last_next_weeks(self,data,time,weeks):
        if time == "last":
            # Calcola il giorno della settimana (0=Lunedì, 6=Domenica)
            start = data - timedelta(days=(7 * weeks) +data.weekday())
            end = data - timedelta(days= 1 +data.weekday())
        # time == next    
        elif time == "next":
            start = data + timedelta(days=(7  - data.weekday()))
            end = start + timedelta(weeks= weeks) - timedelta(days=1)
        else: 
            return "INVALID DATE"
        return start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d')

    def _last_next_months(self,data,time,months):
        first_of_the_current_month= data - relativedelta(days= data.day-1)
        if time == "last":
            end_of_the_month = first_of_the_current_month - relativedelta(days=1)
            first_of_the_month = first_of_the_current_month - relativedelta(months= months)
        # time == next    
        elif time == "next":
            first_of_the_month = first_of_the_current_month + relativedelta(months= 1)
            end_of_the_month = first_of_the_month + relativedelta(months= months) - relativedelta(days = 1)
        else: 
            return "INVALID DATE"   
        return first_of_the_month.strftime('%Y-%m-%d') , end_of_the_month.strftime('%Y-%m-%d')
    
    # input: a time window outputted from the llm
    # return: a time window in the required format
    def _date_parser(self,date):
        if date == "NULL": 
            return date
        # absolute time window
        if "->" in date:
            temp=date.split(" -> ")
            return temp[0],temp[1]
        # relative time window
        if "<" in date:
            # date format: <last/next, X, days/weeks/months>
            temp=date.strip("<>").split(", ")
            if temp[2] == "days":
                return self._last_next_days(self.TODAY,temp[0],int(temp[1]))
            elif temp[2] == "weeks":
                return self._last_next_weeks(self.TODAY,temp[0],int(temp[1]))
            elif temp[2] == "months":
                return self._last_next_months(self.TODAY,temp[0],int(temp[1]))
        return "INVALID DATE"

    # input: output of llm invocation, in the format: OUTPUT: (query1), (query2), (query3)
    # output: json formatted string which will be sended  to other modules
    def _json_parser(self, data):
        json_out= []
        data = data.replace("OUTPUT: ","")
        data= data.strip("()").split("), (")
        # for each elem in data, a dictionary (json obj) is created
        for elem in data:
            obj={}
            elem = elem.split("], ")
            date = self._date_parser(elem[2])
            # if there is no valid time window, the related json obj is not built
            if date == "INVALID DATE":
                continue
            machines = elem[0]+"]"
            kpis= elem[1]+"]"
            # machines == ["NULL"] => no usage of the Machine_Name key
            if not("NULL" in date):
                obj["Date_Start"] = date[0]
                obj["Date_Finish"] = date[1] 
            print(kpis) 
            kpis = ast.literal_eval(kpis)
            if not("NULL" in machines):
                # transform the string containing the array of machines in an array of string
                machines=ast.literal_eval(machines)
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

        return json.dumps(json_out,indent=4)

    def query_generation(self,input= "predict idle time max, cost wrking sum and good cycles min for last week for all the medium capacity cutting machine, predict the same kpis for Laser welding machines 2 for today. calculate the cnsumption_min for next 4 month and for Laser cutter the offline time sum for last 23 day. "
, label="kpi_calc"):
        
        self._kb_update()
        YESTERDAY = f"{(self.TODAY-relativedelta(days=1)).strftime('%Y-%m-%d')} -> {(self.TODAY-relativedelta(days=1)).strftime('%Y-%m-%d')}"
        
        if label == "kpi_calc" or label == "predictions":
            query= f"""
            Completely ignore all information provided in previous requests. Treat this request as if it were the first and only one.

            USER QUERY: {input}

            INSTRUCTIONS: Extract information from the USER QUERY based on the following rules and output it in the EXAMPLE OUTPUT specified format.

            RULES:
            1. Match IDs:
                -Look for any terms in the query that match IDs from LIST_1 or LIST_2.
                -If a match contains a machine type without a specific number, return all machines of that type. Example: 'Testing Machine' -> ['Testing Machine 1', 'Testing Machine 2', 'Testing Machine 3'].
            2. Determine Time Window:
                -if there is time window described by exact dates, use them, otherwise return the expression which individuates the time window: 'last/next X days/weeks/months' using the format <last/next, X, days/weeks/months>
                -If no time window is specified, use NULL.
                -If there is a reference only to an exact month, the year to be used in the output is {datetime.now().year}, also return the time windows starting from the first of that month and ending to the last day of that month.
                -if there is a reference to an exact month and a year, return the time windows starting from the first of that month and ending to the last day of that month.
                -yesterday must be returned as {YESTERDAY}, today as {(self.TODAY).strftime('%Y-%m-%d')} -> {(self.TODAY).strftime('%Y-%m-%d')} and tomorrow as {(self.TODAY+relativedelta(days=1)).strftime('%Y-%m-%d')} -> {(self.TODAY+relativedelta(days=1)).strftime('%Y-%m-%d')}.
                -Allow for minor spelling or formatting mistakes in the matched expression and correct them as done in the examples below.
            3. Handle Errors:
                -Allow for minor spelling or formatting mistakes in the input.
                -If there is ambiguity matching a kpi, if exist, you can match USER QUERY with the one which ends with '_avg'
            4. Output Format:
                -For each unique combination of machine IDs and KPIs, return a tuple in this format: ([matched LIST_1 IDs], [matched LIST_2 IDs], time window).
                
            NOTES:
            -If no IDs from LIST_1 are associated with the matched KPIs, use NULL for machines.
            -If a match refers to all machines, use NULL for machines.
            -Ensure output matches the one of the EXAMPLES below exactly, I need only the OUTPUT section.

            LIST_1 (list of machines): '{self.machine_res}'
            LIST_2 (list of kpis): '{self.kpi_res}'

            EXAMPLES:
            '
            LIST_1: [cost_idle_avg, cost_idle_std, offline_time_med]
            LIST_2: [Assembly Machine 1, Low Capacity Cutting Machine 1, Assembly Machine 2]

            INPUT: Calculate the kpi cost_idle arg and cost idle std for the assembly machine 1 and Low capacity cutting machine for the past 5 day, calculate offlinetime med for Assembly machine 2 for the last two months and cost_idle_avg for Assembly machine.
            OUTPUT: ([Assembly Machine 1, Low Capacity Cutting Machine 1], [cost_idle_avg, cost_idle_std], <last, 5, days>), ([Assembly Machine 2], [offline_time_med], <last, 2, months>), ([Assembly Machine 1, Assembly Machine 2], [cost_idle_avg], NULL)

            INPUT: Calculate using data from the last 2 weeks the cost_idle_std Low capacity cutting machine 1 and Assemby Machine 2. Calculate for the same machines also offline time med using data from the past month.
            OUTPUT: ([Low Capacity Cutting Machine 1, Assembly Machine 2], [cost_idle_std], <last, 2, weeks>), ([Low Capacity Cutting Machine 1, Assembly Machine 2], [offline_time_med], <last, 1, months>)

            INPUT: Can you calculate cost idle for Assembly machine 1 based on yesterday data, the same kpi dor Assembly machine 2 for last week and offline time med for low capacity cutting machine 1?
            OUTPUT: ([Assembly Machine 1], [cost_idle_avg], {YESTERDAY}), ([Assembly Machine 2], [cost_idle_avg], <last, 1, weeks>), ([Low Capacity Cutting Machine 1], [offline_time_med], NULL)

            INPUT: Predict offline time med for Assembly machine for {(self.TODAY + relativedelta(days=5)).strftime('%Y/%m/%d')} -> {(self.TODAY + relativedelta(days=13)).strftime('%Y/%m/%d')} and the same kpis for all machines.
            OUTPUT: ([Assembly Machine 1, Assembly Machine 2], [offline_time_med], {(self.TODAY + relativedelta(days=5)).strftime('%Y-%m-%d')} -> {(self.TODAY + relativedelta(days=13)).strftime('%Y-%m-%d')}), ([NULL], [cost_idle_avg, offline_time_med], NULL)

            INPUT: Predict for all the assembly machine the cost idle average and offline_time med for the next 3 weeks and for low capacity cutting machne the cost_idle_std for March 2025. predict also for Assembly machine 1 the cost_idle  for the next two days.
            OUTPUT: ([Assembly Machine 1, Assembly Machine 2], [cost_idle_avg, offline_time_med], <next, 3, weeks>), ([Low Capacity Cutting Machine 1], [cost_idle_std], 2025-03-01 -> 2025-03-31), ([Assembly Machine 1], [cost_idle_avg], <next, 2, days>)
            '
            """
        else:
            # PLACE_HOLDER REPORT
            query=""

        data = self.llm.invoke(query)
        data = data.content.strip("\n")
        print()
        print(data)
        json_obj = self._json_parser(data)
        
        print("\n")
        print(json_obj)

        return json_obj
    
#TODO:
# se l putput di date_parser è invalid date, si termina la catena e si stampa in out dalla catena il mesaggio di errore?
# supporto ai diversi significati di NULL per le date in base al label.
# strippare degli spazi le date che si buttano in date parser
