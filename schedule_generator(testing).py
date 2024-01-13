from datetime import datetime
from dateutil import parser
from datetime import timedelta
import numpy as np
import calendar
from parsingcourses import CourseScheduler
import copy
#from tkinter import *
#from tkinter import ttk
#import tkinter as tk
#from tkinter import messagebox


def getCourseRawInfo(course_name: str, all_courses: dict) -> tuple:
    '''
    gets the raw time data and course ID for each course
    '''
    dept = course_name.split()[0] #splits the input into the department and number, grabbing the dept
    class_time = all_courses[dept][course_name] #the class section times would be in the course name within the department
    
    if type(class_time) == list: #check if the section times are in lists (otherwise dict) to check if there are labs/discussions
        all_time = [time[0] for time in class_time] #regular section times
        all_class_id = [time[1] for time in class_time] #course ID associated with the regular section times
        
        return (all_time, all_class_id) #return regular course info
    
    else:
        all_reg_time = [time[0] for time in class_time['R']] #regular time if its a dict
        all_reg_id = [time[1] for time in class_time['R']] #regular time ID if its dict
        all_dl_time = [time[0] for time in class_time['DL']] #pull out lab/discussion section times
        all_dl_id_ = [time[1] for time in class_time['DL']] #pull out the lab/discussion section IDs
    
        return (all_reg_time, all_reg_id, all_dl_time, all_dl_id_) #return regular and discussion/lab info

def convert(input_course:list): #test case for convert
    if input_course[0] == 'NA': 
        rearranged_arr = input_course
    else:
        # print(input_course)
        input_mid = int((int(len(input_course)))/2)
        # print(f'In CONVERT FUNCTION: {input_course}')
        date_times =[parser.parse(time) for time in input_course]
        start_list = date_times[0:input_mid]
        end_list = date_times[input_mid::] 
        rearranged_arr = [start_list, end_list]
    return rearranged_arr

def check(current_course, other_course): #test case for compare
    #citation: CHATGPT Query: Write a function that detects the overlap between two python datetimes "
    #current course is in the format [[]] 
    if len(current_course) == 1 or len(other_course) == 1:
        return True
    else:

        for i in range(len(current_course[0])):
            day_comp = current_course[0][i].weekday()
            for k in range(len(other_course[0])):
                day_curr = other_course[0][k].weekday() 
                day_conflict = False
                if day_comp == day_curr:
                    day_conflict = True
                if day_conflict:
                    start_time_1 = current_course[0][i]
                    end_time_1 = current_course[1][i]
                    start_time_2 = other_course[0][k]
                    end_time_2 = other_course[1][k]
                    if (start_time_1 < end_time_2) and (end_time_1 > start_time_2):
                        return False
                    
        return True

def getCourseSchedule(all_courses: dict, desired_courses: list, depts_of_interest = False) -> list: 
    
    available_courses = [] #list of all the possible course combination times
    available_courses_id = [] #list of all the possible course combination IDs
    for course in desired_courses: #loops through courses from the user 
        course_info = getCourseRawInfo(course, all_courses) #pull out the section times and ID for each course
        all_reg_time = course_info[0] #regular section times
        # print(all_reg_time[0])
        all_reg_time_convert = [convert(reg_time) for reg_time in all_reg_time] #use convert function (needs to be fixed)
        all_reg_id = course_info[1] #regular section IDs
        all_dl_time_convert = None #initializes for potential lab/discussion time
        all_dl_id = None #initializes for potential lab/discussion ID
        
        if len(course_info) == 4: #if there is a lab/discussion time, pull those info also
            all_dl_time = course_info[2] #lab/discussion times
            all_dl_time_convert = [convert(dl_time) for dl_time in all_dl_time] #use convert function (needs to be fixed)
            all_dl_id = course_info[3] #lab/discussion IDs
        
        if all_dl_time_convert is not None: #if there are lab/discussion sections
            curr_time_compare = [[reg_time,dl_time] #creates a 2D array to store all the possible regular and lab/disc combinations
                                    for reg_time in all_reg_time_convert
                                    for dl_time in all_dl_time_convert]
            curr_id_compare = [[reg_id,dl_id] 
                                   for reg_id in all_reg_id #creates a 2D array to store all the possible regular and lab/disc comb IDs
                                   for dl_id in all_dl_id]
        else:
            curr_time_compare = [[reg_time] #creates a 2D array (more efficient coding) that lists out all the section times
                                    for reg_time in all_reg_time_convert]
            curr_id_compare = [[reg_id] #creates a 2D array (more efficient coding) that lists out all the section IDs
                                   for reg_id in all_reg_id]

        count = 0 #for testing purposes
        if desired_courses.index(course) != 0: #if it's not the first course being stored
            update_available_courses = [] #initializes the list to store all available time combinations after addition of new course
            update_available_courses_id = [] #initializes the list to store all available combination IDs after addition of new course
            index_for_id_courses = 0 #to track index of which combination to pull ID when needed
            available_courses_id_copy = copy.deepcopy(available_courses_id) #make deep copy of the available combinations
             
            for curr_courses in curr_time_compare: #the combinations for the current course
                addition_courses = [] #course times to add to the available combination
                addition_courses_id = [] #course IDs to add to the available combiniation
                compare_courses = [] #course times that are already in the available combinations
                compare_id = [] #course IDs that are in the available combinations
                index_for_id_course = 0 #to track index of which courses within a curr combination to pull from
                
                for curr_course in curr_courses: #the courses within each current combination
                    a_course_id_index = 0 #tracks the ID of the courses in the available combinations
                    
                    for available_course in copy.deepcopy(available_courses): #goes through the course times in the available combinations
                        a_section_id_index = 0 #tracks the ID of each course within each available combination
                        for available_section in available_course: #for each course time within an availble combination
                            avail_nooverlap = check(curr_course, available_section) #check if the current course time in a combination overlaps with it
                            # print(avail_nooverlap)
                            # print(curr_id_compare[index_for_id_courses][index_for_id_course])
                            # print(available_courses_id_copy[a_course_id_index][a_section_id_index])
                            
                            if index_for_id_course != 0:
                                courses_id = available_courses_id_copy[a_course_id_index]
                                if courses_id not in compare_id:
                                    break
                            
                            if avail_nooverlap: #nooverlap is True
                                curr_id = curr_id_compare[index_for_id_courses][index_for_id_course] #current section ID that works with the combination 
                                
                                if curr_id not in addition_courses_id: #if ID is not already being added, added to the 'to-be-added' list
                                    addition_courses.append(curr_course) #add course time to the list of courses to be added
                                    addition_courses_id.append(curr_id) #add the IDs associated with that
                                   
                                courses_id = available_courses_id_copy[a_course_id_index] #IDs for available combinations
                                
                                if courses_id not in compare_id: #if this combination is not in the possible combination list to be added
                                    compare_courses.append(copy.deepcopy(available_course)) #add course time combination
                                    compare_id.append(courses_id) #add the IDs
                                    
                                a_section_id_index += 1 
                                
                            else: 
                                courses_id = available_courses_id_copy[a_course_id_index]
                                if courses_id in compare_id:
                                    compare_courses.remove(copy.deepcopy(available_course))
                                    compare_id.remove(courses_id)
                                break
                        a_course_id_index += 1
                        
                    index_for_id_course += 1

                comp_id_index = 0 
                compare_courses = copy.deepcopy(compare_courses) #create deepcopies so no elements get manipulated
                compare_id = copy.deepcopy(compare_id)
                addition_courses = copy.deepcopy(addition_courses)
                addition_courses_id = copy.deepcopy(addition_courses_id)     
                
                if len(curr_courses) == len(addition_courses_id): #if there is no overlap
                    
                    for compare_course in compare_courses: #the possible combinations in the available list
                        add_id_index = 0
                        
                        for add_course in addition_courses: #the current possible combinations to be added to the available list
                            compare_course.append(add_course) 
                            compare_id[comp_id_index].append(addition_courses_id[add_id_index])
                            add_id_index += 1
                            
                        update_available_courses.append(compare_course) #add the each updated combinations to the update list
                        update_available_courses_id.append(compare_id[comp_id_index]) #add index
                        # print(update_available_courses_id)
                        comp_id_index += 1
                        
                index_for_id_courses += 1

            available_courses = update_available_courses #after entire iteration, update available combintations
            available_courses_id = update_available_courses_id #update ID
            
            #print(available_courses_id)
            # print(available_courses)
            # count = len(available_courses)
            # print(count)

        
        else:
            available_courses = curr_time_compare
            available_courses_id = curr_id_compare
            
            # print(available_courses_id)
            # print(available_courses)
            # count = len(available_courses)
            # print(count)
        
    return available_courses, available_courses_id
    
# def getDesireCourses(num_entries:int= 3):
    
        
#     main = Tk() #create window
#     main.title('Course Entries')
    
#     num_entries = num_entries
#     labels = [f'Course {i+1}:' for i in range(num_entries)]
#     entries = [tk.Entry(main, width=20) for _ in range(num_entries)]

#     # Pack Entry widgets
#     for i, (label, entry) in enumerate(zip(labels, entries)):
#         label_widget = tk.Label(main, text=label)
#         label_widget.grid(row=i, column=0, padx=5, pady=5, sticky='e')  # 'e' for east (right-align)
#         entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')  # 'w' for west (left-align)

#     # Create a button to get user input
#     button = tk.Button(main, text="Generate Schedule(s)", command=lambda: get_user_input(entries))
#     button.grid(row=len(labels), column = 1, columnspan=2, pady=10, sticky='nsew')
    
#     plus_button = tk.Button(main, text="+", command=lambda:updated_entry_callback(num_entries + 1, main))
#     plus_button.grid(row=len(labels), column=0, pady=10)
    
#     ext = tk.Button(main, text="Exit", command = lambda:end_program(main))
#     ext.grid(row=len(labels)+1, column=1, columnspan=2, pady=10,sticky='nsew')
    
#     minus_button = tk.Button(main, text="-", command=lambda:updated_entry_callback(num_entries - 1, main, add=False))
#     minus_button.grid(row=len(labels)+1, column=0, pady=10, sticky='s')
    
    
#     screen_width = main.winfo_screenwidth()
#     screen_height = main.winfo_screenheight()
#     width = max(entry.winfo_reqwidth() for entry in entries) + 90
#     height = sum(entry.winfo_reqheight() + 10 for entry in entries) + 100
#     x = (screen_width - width) // 2
#     y = (screen_height - height) // 2 - 100
#     main.geometry(f'{width}x{height}+{x}+{y}')
    

    
#     main.mainloop()

# def get_user_input(entries: list):
#     course_file = 'COURSE_DATA_ACTUAL.html'
#     course_object = CourseScheduler(course_file)
#     all_courses = course_object.getAllCourses()
    
#     desired_courses = []
    
#     for entry in entries:
#         desired_course = entry.get().strip()
#         check_format = len(desired_course.split())
#         if desired_course == '':
#             continue
#         elif check_format != 2:
#             return course_error_message(desired_course)
#         else:
#             desired_course = desired_course.upper()
#             if check_course_name(desired_course, all_courses):
#                 desired_courses.append(desired_course)
#             else:
#                 return course_error_message(desired_course)
    
#     if desired_courses == []:
#         empty_entries_error_message()
    
#     else:
#         schedule_window(all_courses, desired_courses)

# def schedule_window(all_courses:dict, desired_courses:list, schedule_option: int= 0):
#     available_time, available_courses_id = getCourseSchedule(all_courses, desired_courses)
#     # print(available_time)
#     # print(available_courses_id)
    
#     if available_courses_id == []:
#         messagebox.showinfo('Info',"A schedule cannot be generated with the inputted courses.")
#     else:
#         schedule_time = available_time[schedule_option]
#         schedule_id = available_courses_id[schedule_option]
#         # print(schedule_time)
#         # print(schedule_id)
#         schedule = Tk()
#         schedule.title('Schedule')
#         weekdays = {'':0,'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5}
        
#         style = ttk.Style(schedule)
#         style.theme_use("clam")
#         style.configure("Treeview.Heading", background="black", foreground="white")
        
#         schedule_table = ttk.Treeview(schedule, columns=list(weekdays), show="headings")
        
#         for i, days in enumerate(list(weekdays)):
#             schedule_table.heading(days, text=days)
#             schedule_table.column(days, anchor="center", width=150)

#         schedule_table.grid(row=0)
        
        
#         for i in range(len(schedule_time)):
#             course_id = schedule_id[i]
#             if schedule_time[i] == ['NA']:
#                 time = [course_id, 'TBA', 'TBA', 'TBA', 'TBA', 'TBA']
#                 item_id = schedule_table.insert('', 0, values=(time))
#                 continue
#             time = [course_id, "", "", "", "", ""]
#             course_start = schedule_time[i][0]
#             course_end = schedule_time[i][1]
#             for j in range(len(course_start)):
#                 # print(course_start[j])
#                 course_day = weekdays[course_start[j].strftime('%A')]
#                 course_time = f"{course_start[j].strftime('%I:%M %p')} - {course_end[j].strftime('%I:%M %p')}"
#                 time[course_day] = course_time
#             item_id = schedule_table.insert('', 0, values=(time))
            
#         tree_height = len(schedule_id)
#         schedule_table.configure(height=tree_height)
        
#         schedule_options = [f'Schedule Option {i+1}' for i in range(len(available_courses_id))]
        
#         selected_option = tk.StringVar(schedule)
#         selected_option.set(schedule_options[schedule_option])  # Set default value
        
#         combobox = ttk.Combobox(schedule, values=schedule_options, textvariable=selected_option)
#         combobox.grid(row=1, column=0,pady=5,padx=20,sticky='w')
#         combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event,combobox,schedule_option, schedule, all_courses, desired_courses))
        
        
#         close = tk.Button(schedule, text="close", command = lambda:end_program(schedule))
#         close.grid(row=2, column=0,pady=3,sticky='n')
        
#         screen_width = schedule.winfo_screenwidth()
#         screen_height = schedule.winfo_screenheight()
#         width = sum(schedule_table.column(days)['width'] for days in weekdays) + 20
#         height = schedule_table.winfo_reqheight() + 70
#         x = (screen_width - width) // 2
#         y = (screen_height - height) // 2 - 100
        
#         schedule.geometry(f'{width}x{height}+{x}+{y}')
#         schedule.mainloop()

        
# def on_select(event, combobox, curr_option, close_window, all_courses, desired_courses):
#     schedule_option = int(combobox.get().split()[2]) - 1
#     if curr_option != schedule_option:
#         end_program(close_window)
#         schedule_window(all_courses, desired_courses, schedule_option)
        

    
# def updated_entry_callback(updated_entry_num, close_window,add=True):
#     if add:
#         end_program(close_window)
#         getDesireCourses(updated_entry_num)
#     else:
#         if updated_entry_num < 3:
#             messagebox.showinfo('Info',"You can't take less than 3 courses!")
#         else:
#             end_program(close_window)
#             getDesireCourses(updated_entry_num)
            
# def check_course_name(desired_course: str, all_courses: dict):
#     dept_name = desired_course.split()[0]
#     if dept_name not in list(all_courses.keys()):
#         return False
#     if desired_course not in all_courses[dept_name]:
#         return False
    
#     return True
    
# def course_error_message(course_error_name: str):
#     messagebox.showinfo('Info',f'{course_error_name} is not found \nPlease check formatting! Make sure to have a space between the department name and the course name!')

# def empty_entries_error_message():
#     messagebox.showinfo('Info','Please enter a course!')

# def end_program(window):
#     window.destroy()
    
# def id_and_course_name_match(all_courses, desired_courses):
#     id_to_course_name = {}
#     for course in desired_courses:
#         dept = course.split()[0]
#         course = all_courses[dept][course]


def main(): 
    course_file = 'COURSE_DATA_ACTUAL.html'
    course_object = CourseScheduler(course_file)
    all_courses = course_object.getAllCourses()
    # getDesireCourses()
    desired_courses = ['DCS 109','DCS 206','ECON 255', 'EDUC 461']

    #getCourseSchedule(all_courses, desired_courses)

    ####################################### ROBUST TESTING ##################################################

    #Test for PHYS 109, CHEM 108, ECON 255, and PHYS 458
    A =  "10220" #uppercase corresponds to class CRN; this is PHYS 109
    a1 = "10221" #lowercase corresponds to lab CRN/discussion section for class of that same letter
    a2 = "10222" 

    B1 = "10888" #this is for CHEM 108
    B2 = "10889"
    B3 = "10890"
    B4 = "10891"

    b1 = "10892" #these are all the CHEM 108 labs
    b2 = "10893"
    b3 = "10894" 
    b4 = "10895" 
    b5 = "10896"
    b6 = "10897"
    b7 = "10898"
    b8 = "11318" 

    C1 = "10733" #ECON 255 class 
    C2 = "10734" 

    D = "10229" #PHYS 458 senior thesis Winter 

    #Below are the expected possibilities for the above classes, calculated by hand 
    pos_list_1 = [A, a2, B1, b1, C1, D]
    pos_list_2 = [A, a2, B1, b2, C1, D]
    pos_list_3 = [A, a2, B1, b6, C1, D]
    pos_list_4 = [A, a2, B3, b1, C1, D]
    pos_list_5 = [A, a2, B3, b2, C1, D]
    pos_list_6 = [A, a2, B3, b6, C1, D]
    pos_list_7 = [A, a2, B4, b1, C1, D]
    pos_list_8 = [A, a2, B4, b2, C1, D]
    pos_list_9 = [A, a2, B4, b6, C1, D]
    full_pos_list_c1 = [pos_list_1, pos_list_2, pos_list_3, pos_list_4, pos_list_5, pos_list_6,
                        pos_list_7, pos_list_8, pos_list_9] #all the possiblility lists with C1
    full_pos_list_c2 = []
    for i in range(len(full_pos_list_c1)):
        copied_list = copy.deepcopy(full_pos_list_c1)
        temp_list = copied_list[i]
        temp_list[4] = C2 #basically, if the element in a sublist of the full position list at index four = C1 (ECON 255 first section),
        #replace with the second section of ECON 255
        full_pos_list_c2.append(temp_list)
    #print(len(full_pos_list_c2))

    full_pos_list = [] 
    #print(f"full_pos_list_c1 is {full_pos_list_c1}")
    for i in range(len(full_pos_list_c1)*2): #creating a composite list of the c1 and c2 full lists
        if i < len(full_pos_list_c1): 
            full_pos_list.append(full_pos_list_c1[i])
        else: 
            full_pos_list.append(full_pos_list_c2[i - len(full_pos_list_c1)]) #append the value at the same index
    #print(f"full pos list is {full_pos_list}")    


    desired_courses_2 = ["PHYS 109", "CHEM 108A", "ECON 255", "PHYS 458"]
    courses, course_id = getCourseSchedule(all_courses, desired_courses_2)
    print("===================================================================================")
    print(f"TESTING {desired_courses_2}")
    print(f"test_case should result in")
    for i in range(len(full_pos_list)): 
        print(f"Possible Schedule Expected is {full_pos_list[i]}")
    print(f"Actual result of running is")
    for i in range(len(course_id)): 
        print(f"Possible Schedule Result is {course_id[i]}")
    print(f"Length of test case should be {len(full_pos_list)}")
    print(f"Length of actual result is {len(course_id)}")

    result = []
    for i in range(len(course_id)): 
        for j in range(len(full_pos_list[i])):
            if course_id[i][j] == full_pos_list[i][j]: #the reason we can do this is because the manual entry and computer
            #entry are the same
                result.append(True)
            else: 
                result.append(False)
    if False not in result: 
        print("TEST PASSED! Every sublist in result has an exact match to a sublist in the expected list")
    else: 
        print("TEST FAILED")

    # desired_courses_3 = ["AFR 458", "AVC 458A", "BIO 458", "BIOC 458"]
    # courses_2, course_id_2 = getCourseSchedule(all_courses, desired_courses_3)       
    # print("===================================================================================")
    # print(f"Testing {desired_courses_3}")
    # expected_list = [["10002", "10952", "10491", "10913"]]
    # print(f"Length of test case is {len(expected_list)}")
    # print(f"Length of actual result is {len(course_id_2)}")
    # result_2 = []
    # result_3 = []
    # for i in range(len(course_id_2)): 
    #     for j in range(len(course_id_2[i])):
    #         if course_id_2[i][j] == expected_list[i][j]: 
    #             result_2.append(True)
    #         else: 
    #             result_3.append(False)
    # if False not in result_2: 
    #     print("TEST PASSED! Every sublist in result has an exact match to a sublist in the expected list")
    # else: 
    #     print("TEST FAILED")  

    # desired_courses_4 = ["ASIA 224", "BIO 213", "CHI 202", "DANC 270B"] 
    # courses_3, course_id_3 = getCourseSchedule(all_courses, desired_courses_4)
    # print("===================================================================================")
    # print(f"Testing {desired_courses_4}")
    # expected_list_2 = [["10569", "10481", "10573", "10613"]]
    # print(f"Length of test case is {len(expected_list_2)}")
    # print(f"Length of actual result is {len(course_id_3)}")
    
    # print(course_id_3)
    # for i in range(len(course_id_3)): 
    #     for j in range(len(course_id_3[i])):
    #         if course_id_3[i][j] == expected_list_2[i][j]: 
    #             result_3.append(True)
    #         else: 
    #             result_3.append(False)
    # if False not in result_3: 
    #     print("TEST PASSED! Every sublist in result has an exact match to a sublist in the expected list")
    # else: 
    #     print("TEST FAILED")     
    
    desired_courses_5 = ["BIO 195J", "CMS 107", "EACS 220", "ECON 250"] 
    courses_4, course_id_4 = getCourseSchedule(all_courses, desired_courses_5)
    print("===================================================================================")
    
    print(f"TESTING {desired_courses_5}")
    print('test_case should result in')
    print(f'Possible Schedule Expected is []')
    print('Actual result of running is')
    print(f"Possible Schedule Result is {course_id_4}")
    expected_list_3 = [[]]
    print(f"Length of test case is {len(expected_list_3)}")
    print(f"Length of actual result is {len(course_id_4)}")
    result_4 = []
    print(result_4)
    result_4.append(course_id_4 == expected_list_3[0])
    if False not in result_4: 
        print("TEST PASSED! Every sublist in result has an exact match to a sublist in the expected list")
    else: 
        print("TEST FAILED")   
    
    

if __name__ == "__main__":
    main()