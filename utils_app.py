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
        
    @staticmethod
    def get_incorrect_declinations_in_imenica() -> tuple:
        EXPECTED_DECLINATIONS = 14
        def check_number_of_declinations(line: str) -> int:
            pos = line.find("(")
            if pos == -1:
                return 0
            line = line[pos:]
            
            pos = line.find(",")
            if pos == -1:
                return 0
            line = line[pos + 1:]
            
            pos = line.find(",")
            if pos == -1:
                return 0
            line = line[pos + 1:]
            
            line = line.strip(" ,\"'()")
            return len([x for x in line.split(",") if x.strip()])

        if not os.path.exists("definition_cls.py"):
            return None
        
        with open("definition_cls.py", "r", encoding="utf-8") as file:
            content = file.read()
        
        code_list = [x for x in content.splitlines()]

        message = ""
        arguments = []
        for ind, line in enumerate(code_list):
            line = line.strip()

            if line.startswith("decl = self._join_pref_base_suff") and check_number_of_declinations(line) != EXPECTED_DECLINATIONS:
                message += f"Line:{ind + 1}:Decl={check_number_of_declinations(line)}: {line}\n"
            if line.startswith("decl_p = self._join_pref_base_suff") and check_number_of_declinations(line) != EXPECTED_DECLINATIONS:
                message += f"Line:{ind + 1}:Decl={check_number_of_declinations(line)}: {line}\n"

        if message:
            message = "Incorrect declinations in module #1 in method #2, Expected: #3:\n" + message
            arguments.append("definition_cls.py")
            arguments.append("imenica")
            arguments.append(EXPECTED_DECLINATIONS)
            return (message.strip(), arguments)

        return None



