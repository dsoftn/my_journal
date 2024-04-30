from typing import Union, Any
import os


class ApplicationSourceCode:
    
    @staticmethod
    def get_class_functions_duplicates_message() -> Union[tuple, None]:
        def get_source_file_lines(file_name: str) -> list:
            lines = []
            with open(file_name, "r", encoding="utf-8") as file:
                for line in file:
                    lines.append(line)
            return lines
        
        result = []
        for item in os.listdir():
            func_list = []
            current_class = None
            prefix = ""
            if item.split(".")[-1].lower() in ("py", "pyw"):
                for line in get_source_file_lines(item):
                    if line.strip().startswith("class "):
                        current_class = line.split("class ")[1].split("(")[0]
                        current_class = current_class.strip(" :")
                        func_list = []
                    if line.strip().startswith("@"):
                        prefix = line.strip() + "::"
                    if line.strip().startswith(("def ", "async def ")):
                        current_func = prefix + line.split("def ")[1].split("(")[0].strip()
                        prefix = ""
                        if current_func not in func_list:
                            func_list.append(current_func)
                        else:
                            result.append([item, current_class, current_func])

        if not result:
            return None
        
        # Create message
        message = "Duplicate functions found in source code:\n"
        arguments = []
        count = 1
        for item in result:
            message += f"CLASS: #{count}"
            arguments.append(item[1])
            count += 1
            message += f"   FUNCTION: #{count}"
            arguments.append(item[2])
            count += 1
            message += f"   FILE: #{count}\n"
            arguments.append(item[0])
            count += 1

        return (message, arguments)
        



