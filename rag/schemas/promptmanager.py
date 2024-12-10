import os
import re
from langchain_core.prompts import PromptTemplate

class PromptManager:
    """
    Initializes the PromptManager to load and manage task-specific prompts.

    Args:
        prompts_dir (str): The directory path containing prompt files.

    Attributes:
        prompts_dir (str): The directory path for loading prompt files.
        prompts (dict): A dictionary to store prompts by task name.
        switcher (dict): A dictionary to map classification labels to task names.

    Methods:
        load_prompts: Loads all prompts from the directory.
        get_prompt: Retrieves the prompt for a specific task based on the label.
        convert_string_to_prompt_template: Converts a string into a langchain prompt template.
        label_to_task_name: Converts the classification label into a task name.
    """
    def __init__(self, prompts_dir):
        """
        Initializes the manager with the directory containing prompt files.

        Args:
            prompts_dir (str): The directory path containing prompt files.
        """
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self.load_prompts()
        self.switcher = {
            "predictions": "calculation_and_forecasting",
            "kpi_calc": "calculation_and_forecasting",
            "new_kpi": "kpi_generation",
            "report": "report",
            "dashboard": "dashboard_generation",
            "translate": "translate",
            "get_language": "get_language"
        }

    def load_prompts(self):
        """
        Loads all prompts from the specified directory.

        This function reads all `.txt` files from the directory and stores the prompt
        content in a dictionary where the key is the task name (filename) and the value is the prompt text.
        """
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".txt"):
                task_name = os.path.splitext(filename)[0]
                with open(os.path.join(self.prompts_dir, filename), 'r') as file:
                    self.prompts[task_name] = file.read().strip()

    def get_prompt(self, label):
        """
        Retrieves the prompt for a specific task based on the classification label.

        Args:
            label (str): The classification label for the task.

        Returns:
            PromptTemplate: The prompt template for the specified task.

        Raises:
            ValueError: If no prompt is found for the given label.
        """
        task_name = self.label_to_task_name(label)
        try:
            prompt = self.prompts[task_name]
        except KeyError:
            raise ValueError(f"No prompt found for task: {task_name}")

        prompt = self.convert_string_to_prompt_template(prompt)
        return prompt

    def convert_string_to_prompt_template(self, template_string):
        """
        Converts a string into a langchain prompt template.

        Args:
            template_string (str): The string representing the prompt.

        Returns:
            PromptTemplate: The langchain prompt template created from the string.
        """
        # Find all placeholders in the string (e.g., {USER_QUERY}, {_CONTEXT_})
        input_variables = re.findall(r"{(_\w+?_)}", template_string)

        # Create the PromptTemplate object
        prompt_template = PromptTemplate(
            input_variables=input_variables,
            template=template_string
        )
        return prompt_template

    def label_to_task_name(self, label):
        """
        Converts the classification label into a task name.

        Args:
            label (str): The classification label to convert.

        Returns:
            str: The task name corresponding to the given label.
        """
        return self.switcher.get(label, label)