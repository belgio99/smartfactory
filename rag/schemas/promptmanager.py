"""
USAGE:
- Initialize the PromptManager with the path to the directory containing prompt files.    
- Get a prompt with get_prompt for a specific task by providing the classification label.
- If needed reload the prompts from the directory with the load_prompt function.
"""


import os
import re
from langchain_core.prompts import PromptTemplate


class PromptManager:
    def __init__(self, prompts_dir):
        """Initialize the manager with the directory containing prompt files.
        
        :param prompts_dir: The directory path containing prompt files."""
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self.load_prompts()
        self.switcher = {
            "predictions": "calculation_and_forecasting",
            "kpi_calc": "calculation_and_forecasting",
            "new_kpi": "kpi_generation",
            "report": "report",
            "dashboard": "dashboard_generation",
            "translate": "translate"
            }
    
    def load_prompts(self):
        """Load all prompts from the directory."""
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".txt"):
                task_name = os.path.splitext(filename)[0]
                with open(os.path.join(self.prompts_dir, filename), 'r') as file:
                    self.prompts[task_name] = file.read().strip()
    
    def get_prompt(self, label):
        """Return a langchain prompt for a specific task.
        
        :param task_name: The string name of the task to retrieve the prompt for."""
        task_name = self.label_to_task_name(label)
        try:
            prompt = self.prompts[task_name]
        except KeyError:
            raise ValueError(f"No prompt found for task: {task_name}")

        prompt = self.convert_string_to_prompt_template(prompt)
        return prompt

    def convert_string_to_prompt_template(self, template_string):
        """
        Converts a string prompt in a langchain prompt.
        
        :param template_string: The string prompt to convert.
        """
        # Trova tutti i segnaposto nella stringa (es. {USER_QUERY}, {_CONTEXT_})
        input_variables = re.findall(r"{(_\w+?_)}", template_string)

        # Crea l'oggetto PromptTemplate
        prompt_template = PromptTemplate(
            input_variables=input_variables,
            template=template_string
        )
        return prompt_template
    
    def label_to_task_name(self, label):
        """Convert the classification label to a task name.
        
        :param label: The label to convert."""
        return self.switcher.get(label, label)