# скрипт для директорії "розібрати". ДЗ модуль 6

from re import sub
from sys import argv, exit
from shutil import move, unpack_archive
from os import path, rename, mkdir, listdir, rmdir, remove

# словник для транслітерації
CYR_TO_LAT = {1072: "a", 1040: "A", 1073: "b", 1041: "B", 1074: "v", 1042: "V", 1075: "h", 1043: "H", 
              1169: "g", 1168: "G", 1076: "d", 1044: "D", 1077: "e", 1045: "E", 1108: "je", 1028: "JE", 
              1078: "zh", 1046: "ZH", 1079: "z", 1047: "Z", 1080: "y", 1048: "Y", 1110: "i", 1030: "I", 
              1111: "ji", 1031: "JI", 1081: "j", 1049: "J", 1082: "k", 1050: "K", 1083: "l", 1051: "L", 
              1084: "m", 1052: "M", 1085: "n", 1053: "N", 1086: "o", 1054: "O", 1087: "p", 1055: "P", 1088: "r", 
              1056: "R", 1089: "s", 1057: "S", 1090: "t", 1058: "T", 1091: "u", 1059: "U", 1092: "f", 1060: "F", 
              1093: "h", 1061: "H", 1094: "ts", 1062: "TS", 1095: "ch", 1063: "CH", 1096: "sh", 1064: "SH", 
              1097: "sch", 1065: "SCH", 1100: "", 1068: "", 1102: "yu", 1070: "YU", 1103: "ya", 1071: "YA", 
              1105: "jo", 1025: "JO", 1098: "", 1066: "", 1099: "y", 1067: "Y", 1101: "e", 1069: "E"}

# формати файлів
ARCHIVES = ("ZIP", "GZ", "TAR")
AUDIO = ("MP3", "OGG", "WAV", "AMR", "FLAC", "MID", "WMA")
DOCUMENTS = ("DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX", "ODT", "LOG", "NFO")
IMAGES = ("JPEG", "PNG", "JPG", "SVG", "WEBP")
VIDEO = ("AVI", "MP4", "MOV", "MKV", "WEBM")

# директорії для відсортованих файлів
SORTED_DIRS = ("archives", "audio", "documents", "images", "video", "others")


def create_dirs_for_sorted_files(path_to_dir: str) -> None:
    
    for current_dir in SORTED_DIRS:

        current_path = path.join(path_to_dir, current_dir)
        
        if path.exists(current_path):

            new_dir_name = get_new_item_name(path_to_dir, current_dir)
            rename(current_path, new_dir_name)

        mkdir(current_path)


def delete_empty_dirs_for_sorted_files(path_to_dir: str) -> None:
    
    for sort_dir in SORTED_DIRS:

        current_item = path.join(path_to_dir, sort_dir)

        if len(listdir(current_item)) == 0:
            rmdir(current_item)


# отримаємо шлях до директорії, яку треба сортувати
def get_dir_path() -> str:

    # спочатку спробуємо перевірити параметр командного рядка...
    if len(argv) != 2:
        
        print("Error: Can't get directory path from command line.")

    else:

        dir_path = argv[1]
        if path.exists(dir_path):
            return dir_path
        else:
            print("Error: Directory path from command line is incorrect.")
    
    dir_path = ""

    # ...якщо параметр відсутній або неправильний, то спробуємо дати користувачу можливість вказати шлях
    while not path.exists(dir_path):
        
        dir_path = input("Input correct path to directory or press [Enter] to exit the script: ")
        
        if dir_path == "":
            exit("Script has been finished witout completing task at user request.")

    return dir_path


def get_filename(input_string: str) -> str:

    return input_string[:input_string.rfind(".")]


def get_filetype(input_string: str) -> str:

    return input_string[input_string.rfind(".") + 1:]


# створює нове ім'я для файла чи директорії, якщо при створенні чи переміщенні цільовий об'єкт вже існує
def get_new_item_name(path_to_dir: str, existing_item: str) -> str:

    n = 1

    while path.exists(path.join(path_to_dir, existing_item + str(n))):
        n += 1

    return path.join(path_to_dir, existing_item + str(n))


def main() -> None:

    global file_types_counter
    global file_types_found
    global directory_in_str
    global all_file_types
    
    file_types_found = set()
    file_types_counter = [0, 0, 0, 0, 0, 0]

    all_file_types = []
    all_file_types.extend(ARCHIVES)
    all_file_types.extend(AUDIO)
    all_file_types.extend(DOCUMENTS)
    all_file_types.extend(IMAGES)
    all_file_types.extend(VIDEO)

    directory_in_str = get_dir_path()

    create_dirs_for_sorted_files(directory_in_str)
    process_dir(directory_in_str)   #основна функція, яка викликається рекурсивно для вкладених директорій
    unpack_archives(path.join(directory_in_str, SORTED_DIRS[0]))
    delete_empty_dirs_for_sorted_files(directory_in_str)    # видаляємо директорії, якщо не було якогось типу файлів

    known_types, unknown_types = sort_file_types(file_types_found)

    # записуємо у файл інформацію щодо провередного сортування
    with open(path.join(directory_in_str, "sort_info.txt"), 'w') as fh:

        for i in range(0, 6):
            fh.write(f"{SORTED_DIRS[i]} = {file_types_counter[i]} file(s)\n")

        fh.write(22 * "-" + "\n")
        fh.write(f"total = {sum(file_types_counter)} file(s)\n")
        
        fh.write(f"\nKnown file type(s): {', '.join(known_types) or 'None'}\n")
        fh.write(f"\nUnknown file type(s): {', '.join(unknown_types) or 'None'}")

    print("Script completed successfully!")


def move_item(source: str, target_path: str, target_item: str) -> None:

    target = path.join(target_path, target_item)

    if path.exists(target):
        target = get_new_item_name(target_path, get_filename(target_item)) + "." + get_filetype(target_item)

    move(source, target)


def normalize(input_string: str) -> str:
    
    # перетворюємо кирилицю на латиницю
    input_string = input_string.translate(CYR_TO_LAT)

    # замінюємо усі символи на підкреслення, окрім  цифр і латинських літер
    input_string = sub(r"[^a-zA-Z0-9_]", "_", input_string)

    return input_string


def process_dir(path_to_dir: str, sorted_dirs = SORTED_DIRS) -> None:

    global file_types_found

    # якщо при переборі об'єктів знаходимо пусту директорію - видаляємо
    if len(listdir(path_to_dir)) == 0:
        rmdir(path_to_dir)
        return None     # лише для того, щоб перервати виконання

    for item_name in listdir(path_to_dir):

        current_item = path.join(path_to_dir, item_name)

        new_filename = normalize(get_filename(item_name)) + "." + get_filetype(item_name)

        # якщо поточний об'єкт - директорія...
        if path.isdir(current_item):

            # ...переходимо до наступного об'єкту, якщо ця директорія для сортованих файлів
            if item_name in sorted_dirs:
                continue

            # ...рекурсивно викликаємо функцію, щоб обробити вкладену директорію
            process_dir(current_item)

        else:
            # переміщуємо файли
            if get_filetype(item_name).upper() in ARCHIVES:
                move_item(current_item, path.join(directory_in_str, sorted_dirs[0]), new_filename)
                file_types_counter[0] += 1

            elif get_filetype(item_name).upper() in AUDIO:
                move_item(current_item, path.join(directory_in_str, sorted_dirs[1]), new_filename)
                file_types_counter[1] += 1

            elif get_filetype(item_name).upper() in DOCUMENTS:
                move_item(current_item, path.join(directory_in_str, sorted_dirs[2]), new_filename)
                file_types_counter[2] += 1

            elif get_filetype(item_name).upper() in IMAGES:
                move_item(current_item, path.join(directory_in_str, sorted_dirs[3]), new_filename)
                file_types_counter[3] += 1

            elif get_filetype(item_name).upper() in VIDEO:
                move_item(current_item, path.join(directory_in_str, sorted_dirs[4]), new_filename)
                file_types_counter[4] += 1

            else:                                 # OTHERS
                move_item(current_item, path.join(directory_in_str, sorted_dirs[5]), new_filename)
                file_types_counter[5] += 1
            
            file_types_found.add(get_filetype(item_name))
    
    # видаляємо пусту директорію після того, як перемістили з неї усі файли
    if path_to_dir != directory_in_str:
        rmdir(path_to_dir)


# розділяємо знайдені типи файлів на відомі і невідомі
def sort_file_types(file_types_found: set) -> set:

    known = set()
    unknown = set()

    for file_type in file_types_found:

        if file_type.upper() in all_file_types:
            known.add(file_type)
        else:
            unknown.add(file_type)

    return known, unknown
            


def unpack_archives(path_to_dir: str) -> None:

    if len(listdir(path_to_dir)) == 0:
        return None # лише для того, щоб перервати виконання, якщо у цільовій директорії немає жодного архіву
    
    for filename in listdir(path_to_dir):

        try:  
            unpack_archive(path.join(path_to_dir, filename), path.join(path_to_dir, get_filename(filename)), get_filetype(filename))
        except Exception as ex:
            file_types_counter[0] -= 1

        remove(path.join(path_to_dir, filename))


if __name__ == "__main__":
    main()