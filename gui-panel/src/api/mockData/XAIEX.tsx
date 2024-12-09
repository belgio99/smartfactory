import {XAISources} from "../../components/ChatAssistant/ChatComponents";


const example = [XAISources.decode(JSON.parse("{\n" +
    "    \"reference_number\": 1,\n" +
    "    \"context\": \"El Sol es la estrella en el centro del sistema solar.\",\n" +
    "    \"original_context\": \"El Sol es la estrella en el centro del sistema solar.\",\n" +
    "    \"source_name\": \"Spanish Article\"\n" +
    "  }")),
    XAISources.decode(JSON.parse("{\n" +
        "    \"reference_number\": 2,\n" +
        "    \"context\": \"L'atmosph\u00e8re terrestre est cruciale pour la vie sur Terre.\",\n" +
        "    \"original_context\": \"L'atmosph\u00e8re terrestre est cruciale pour la vie sur Terre.\",\n" +
        "    \"source_name\": \"French Article\"\n" +
        "  }")),
    XAISources.decode(JSON.parse(" {\n" +
        "    \"reference_number\": 3,\n" +
        "    \"context\": \"Die industrielle Revolution ver\u00e4nderte Gesellschaften radikal.\",\n" +
        "    \"original_context\": \"Die industrielle Revolution ver\u00e4nderte Gesellschaften radikal.\",\n" +
        "    \"source_name\": \"German Article\"\n" +
        "  }")),
    XAISources.decode(JSON.parse("{\"reference_number\":4,\"context\":\"\\n\\\"Machine_name\\\":\\\"Machine_A\\\"\\n\\\"KPI_name\\\":\\\"Temperatura\\\"\\n\\\"Predicted_value\\\":\\\"22\\\"\\n\\\"Measure_unit\\\":\\\"Celsius\\\"\\n\\\"Date_prediction\\\":\\\"12/12/2024\\\"\\n\\\"Forecast\\\":\\\"True\\\"\",\"original_context\":\"[{\\\"Machine_name\\\":\\\"Machine_A\\\",\\\"KPI_name\\\":\\\"Temperatura\\\",\\\"Predicted_value\\\":\\\"22\\\",\\\"Measure_unit\\\":\\\"Celsius\\\",\\\"Date_prediction\\\":\\\"12/12/2024\\\",\\\"Forecast\\\":true},{\\\"Machine_name\\\":\\\"Machine_B\\\",\\\"KPI_name\\\":\\\"Pression\\\",\\\"Predicted_value\\\":\\\"1012\\\",\\\"Measure_unit\\\":\\\"hPa\\\",\\\"Date_prediction\\\":\\\"13/12/2024\\\",\\\"Forecast\\\":true}]\",\"source_name\":\"JsonData\"}"))
]


export default example