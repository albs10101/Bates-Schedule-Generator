from dateutil import parser
from parsingcourses import CourseScheduler
import copy
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox


def getCourseRawInfo(course_name: str, all_courses: dict) -> tuple:
    '''
    Gets the raw time data and course ID for each course
    Parameters: 
        Course_name: the course name
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
    Returns:
        a tuple containting the following lists:
            all_reg_time: time of regular sections
            all_reg_id: id for those regular sections
            all_dl_time: time of lab sections
            all_dl_id: id for those lab sections
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
        all_dl_id = [time[1] for time in class_time['DL']] #pull out the lab/discussion section IDs
    
        return (all_reg_time, all_reg_id, all_dl_time, all_dl_id) #return regular and discussion/lab info

def convert(input_course:list) -> list: 
    '''
    A function that converts a list of start and end times for a section into datetime objects
    Parameters: 
        input_course: a list that has all the start time infront and end time behind
    Retrun:
        rearranged_arr: a list with two lists
            start: the start times as datetime objects
            end: the end times as datetime objects
    '''
    if input_course[0] == 'NA': #check for courses with time TBA
        rearranged_arr = input_course
    else: 
        input_mid = int((int(len(input_course)))/2) #split array into two lists [start] and [end]
        date_times =[parser.parse(time) for time in input_course]
        start_list = date_times[0:input_mid]
        end_list = date_times[input_mid::] 
        rearranged_arr = [start_list, end_list] #format for return
    return rearranged_arr

def check(current_course: list, other_course: list) -> bool: #test case for compare
    #citation: CHATGPT Query: Write a function that detects the overlap between two python datetimes "
    #current course is in the format [[]] 
    '''
    Takes into two courses and comapare their datetime objects and outputs a bool expression to indicate overlapping 
    Parameters:
        current_course: a list containing two lists. The start datetime objects and end datetime objects
        other_course: another list containing two lists. The start datetime objects and end datetime objects
    Return:
        a bool expression, either True if courses don't overlap or False if the courses overlap
    '''
    if len(current_course) == 1 or len(other_course) == 1: #check if any of the courses have TBA time
        return True
    else:

        for i in range(len(current_course[0])):
            day_comp = current_course[0][i].weekday()
            for k in range(len(other_course[0])):
                day_curr = other_course[0][k].weekday() 
                day_conflict = False
                if day_comp == day_curr: #check if the courses have the same day of the week
                    day_conflict = True
                if day_conflict: #if there is day conflict then compare the time within the day
                    start_time_1 = current_course[0][i]
                    end_time_1 = current_course[1][i]
                    start_time_2 = other_course[0][k]
                    end_time_2 = other_course[1][k]
                    if (start_time_1 < end_time_2) and (end_time_1 > start_time_2): #checks if the time conflicts using bool expressions
                        return False 
                    
        return True

def getCourseSchedule(all_courses: dict, desired_courses: list) -> list: 
    '''
    Takes a list of desired courses and outputs the combinations of course sections that work in a list.
    Parameters: 
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
        desired_courses: a list containing all the courses the user inputted
    Return: 
        available_courses: a list of the possible combinations of the user inputted course sections
        available_courses_id: a list of IDs that corresponds to those combinations
    '''
    
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
                            
                            if index_for_id_course != 0: #if its not the first curr course in a possible curr combination
                                courses_id = available_courses_id_copy[a_course_id_index] 
                                if courses_id not in compare_id: #if available course combination is not already registered, break this loop
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
                                if courses_id in compare_id: #remove the courses in the combination that was already added in the potential combination list
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
                
                if len(curr_courses) == len(addition_courses_id): #only add if the current course section combination has no overlaps 
                    
                    for compare_course in compare_courses: #the possible combinations in the available list
                        add_id_index = 0
                        
                        for add_course in addition_courses: #the current possible combinations to be added to the available list
                            compare_course.append(add_course) 
                            compare_id[comp_id_index].append(addition_courses_id[add_id_index])
                            add_id_index += 1
                            
                        update_available_courses.append(compare_course) #add the each updated combinations to the update list
                        update_available_courses_id.append(compare_id[comp_id_index]) #add the corresponding ID numbers of the course combinations to the update list
                        comp_id_index += 1
                        
                index_for_id_courses += 1

            available_courses = update_available_courses #after entire iteration, update available combintations
            available_courses_id = update_available_courses_id #update ID
            
            # print(available_courses_id) #for testing
            # print(available_courses) #for testing
            # count = len(available_courses) #for testing
            # print(count) #for testing

        
        else:
            available_courses = curr_time_compare
            available_courses_id = curr_id_compare
            
            # print(available_courses_id) #for testing
            # print(available_courses) #for testing
            # count = len(available_courses) #for testing
            # print(count) #for testing
        
    return available_courses, available_courses_id
    
def getDesireCourses(course_file: str, num_entries:int= 3) -> None:
    '''
    Creates a window for users to put in their courses
    Parameters:
        num_entries: a integer that represents the amount of entry boxes to display. The default is set to 3
        course_file: the .html file name
    Return:
        None
    '''
        
    main = Tk() #create window
    main.title('Course Entries')
    
    labels = [f'Course {i+1}:' for i in range(num_entries)] #create the labels for the user entries
    entries = [tk.Entry(main, width=20) for _ in range(num_entries)] #the actual entry box

    # Pack Entry widgets
    for i, (label, entry) in enumerate(zip(labels, entries)): #format
        label_widget = tk.Label(main, text=label)
        label_widget.grid(row=i, column=0, padx=5, pady=5, sticky='e')  # 'e' for east (right-align)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')  # 'w' for west (left-align)

    # Create a button to get user input
    button = tk.Button(main, text="Generate Schedule(s)", command=lambda: get_user_input(entries, course_file)) #the lambda ensures that the function gets executed only if its clickled on
    button.grid(row=len(labels), column = 1, columnspan=2, pady=10, sticky='nsew')
    
    #create a button to add more courses
    plus_button = tk.Button(main, text="+", command=lambda:updated_entry_callback(num_entries + 1, main, course_file))
    plus_button.grid(row=len(labels), column=0, pady=10)
    
    #create a button to exit window
    ext = tk.Button(main, text="Exit", command = lambda:end_program(main))
    ext.grid(row=len(labels)+1, column=1, columnspan=2, pady=10,sticky='nsew')
    
    #createl a button to remove a course
    minus_button = tk.Button(main, text="-", command=lambda:updated_entry_callback(num_entries - 1, main, course_file, add=False))
    minus_button.grid(row=len(labels)+1, column=0, pady=10, sticky='s')
    
    #format screen width and open it at center of screen
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    width = max(entry.winfo_reqwidth() for entry in entries) + 90
    height = sum(entry.winfo_reqheight() + 10 for entry in entries) + 100
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 100
    main.geometry(f'{width}x{height}+{x}+{y}')
    

    
    main.mainloop()

def get_user_input(entries: list, course_file: str) -> None:
    '''
    Takes in the entries, check the formatting and validity of the courses,
    and format it into a list of desired courses.
    Parameters:
        entries: the entry information inputted by the user
        course_file: the .html file name
    Return:
        None
    '''
    course_object = CourseScheduler(course_file)
    all_courses = course_object.getAllCourses()
    
    desired_courses = []
    
    for entry in entries:
        desired_course = entry.get().strip() #removes accidental empty space
        check_format = len(desired_course.split()) #takes length
        
        if desired_course == '': #if there is nothing inputted, skip entry
            continue
        elif check_format != 2: #if the entry does not have a department and course number components when split
            return course_error_message(desired_course) #outputs error message
        else:
            desired_course = desired_course.upper() #caps everything
            if check_course_name(desired_course, all_courses): #check if course is in dict
                desired_courses.append(desired_course) #if it is, append to desire list
            else:
                return course_error_message(desired_course) #if not output error message
    
    if desired_courses == []: #if desired course list is empty return message
        empty_entries_error_message()
    
    else:
        schedule_window(all_courses, desired_courses) #generate schedule

def schedule_window(all_courses:dict, desired_courses:list, schedule_option:int= 0) -> None:
    '''
    The function takes in the list of the desired courses and outputs a window 
    displaying a schedule for one of possible course combination options
    Parameters:
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
        desired_courses: a list containing all the courses the user inputted
        schedule_option: an integer indicating which course combination to display as the schedule. The default is set to the first one
    Return:
        None
    '''
    available_time, available_courses_id = getCourseSchedule(all_courses, desired_courses) #gets the available combinations (as elements) and its respective IDs
    
    if available_courses_id == []: #if the output is no combination, display error message
        messagebox.showinfo('Info','A schedule cannot be generated with the inputted courses.')
    else:
        schedule_time = available_time[schedule_option] #choose combination
        schedule_id = available_courses_id[schedule_option]
        id_name_conversion = id_and_course_name_match(all_courses, desired_courses) #the possible course names with IDs as keys

        schedule = Tk()
        schedule.title('Schedule')
        weekdays = {'Course Name (Course ID)':0,'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5} #dictionary for column names
        
        style = ttk.Style(schedule) #change style of the columns
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="black", foreground="white")
        
        schedule_table = ttk.Treeview(schedule, columns=list(weekdays), show="headings") #create table using Treeview
        
        for i, days in enumerate(list(weekdays)): #create the columns in Treeview
            schedule_table.heading(days, text=days)
            schedule_table.column(days, anchor="center", width=165)

        schedule_table.grid(row=0) #place the table
        
        
        for i in range(len(schedule_time)): #course in combination
            course_id = schedule_id[i]
            course_name = id_name_conversion[course_id]
            course_info_formatted = f'{course_name} ({course_id})' #format course name
            
            if schedule_time[i] == ['NA']: #if course time is NA (meaning its TBA), output TBA in row
                time = [course_info_formatted, 'TBA', 'TBA', 'TBA', 'TBA', 'TBA']
                item_id = schedule_table.insert('', 0, values=(time))
                continue
            time = [course_info_formatted, "", "", "", "", ""] #if not initialize blank column
            course_start = schedule_time[i][0] #the start time list
            course_end = schedule_time[i][1] #the end time list
            for j in range(len(course_start)):
                course_day = weekdays[course_start[j].strftime('%A')] #grabs the day of the week
                course_time = f"{course_start[j].strftime('%I:%M %p')} - {course_end[j].strftime('%I:%M %p')}" #converts the rest from datetime back to readable string format
                time[course_day] = course_time #update the list that will be passed into insert row
            item_id = schedule_table.insert('', 0, values=(time)) #add row
            
        tree_height = len(schedule_id) #the tree height will be dependent on the amount of courses
        schedule_table.configure(height=tree_height) 
        
        schedule_options = [f'Schedule Option {i+1}' for i in range(len(available_courses_id))] #options for dropdown menu
        
        selected_option = tk.StringVar(schedule) 
        selected_option.set(schedule_options[schedule_option])  # Set the default selected value to be the combination option
        
        combobox = ttk.Combobox(schedule, values=schedule_options, textvariable=selected_option) # create the actual drop down menu
        combobox.grid(row=1, column=0,pady=5,padx=20,sticky='w') #place drop-down menu in the window
        combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event,combobox,schedule_option, schedule, all_courses, desired_courses)) #bind function to when an option gets selected
        
        
        close = tk.Button(schedule, text="close", command = lambda:end_program(schedule)) #close button that closes the window
        close.grid(row=2, column=0,pady=3,sticky='n')
        
        #format the window size and placement
        screen_width = schedule.winfo_screenwidth() 
        screen_height = schedule.winfo_screenheight()
        width = sum(schedule_table.column(days)['width'] for days in weekdays) + 20
        height = schedule_table.winfo_reqheight() + 70
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 100
        
        schedule.geometry(f'{width}x{height}+{x}+{y}')
        schedule.mainloop()

        
def on_select(event: tk, combobox: tk, curr_option: int, close_window: tk, all_courses: dict, desired_courses: list) -> None:
    '''A function that closes the current schedule window and open another schedule window that displays the selected option
    Paremeters:
        event: a tk combobox default parameter that indicates event
        combobox: a tk object that returns the selected option string
        curr_option: an integer that represents the current option number
        close_window: the current window that will close if certain conditions are met
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
        desired_courses: a list containing all the courses the user inputted
    Return:
        None
    '''
    schedule_option = int(combobox.get().split()[2]) - 1 #grabs the schedule option selected by user
    if curr_option != schedule_option: #compares the selected option with the current option of the window
        end_program(close_window) #if its different close current window
        schedule_window(all_courses, desired_courses, schedule_option) #open new one displaying the selected option
        

    
def updated_entry_callback(updated_entry_num: int, close_window: tk, course_file: str, add:bool= True) -> None:
    '''
    A function that updates the user input window with the correct number of input boxes
    Parameter:
        updated_entry_num: the amount of entry boxes
        close_window: the current window
        add: a bool expression that indicates whether to add or subtract
        course_file: the .html file name
    Return:
        None
    '''
    if add:
        end_program(close_window) #close current window
        getDesireCourses(course_file, updated_entry_num) #open new window with correct user entry boxes
    else:
        if updated_entry_num < 3: #if less than 3 boxes as entry number, output error message
            messagebox.showinfo('Info',"You can't take less than 3 courses!")
        else:
            end_program(close_window) #if not update window
            getDesireCourses(course_file, updated_entry_num)
            
def check_course_name(desired_course: str, all_courses: dict) -> bool:
    '''
    Check if course name is in dictionary of all courses
    Parameters:
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
        desired_courses: a list containing all the courses the user inputted
    Return:
        a boolean expression that indicates whether course name entered is a valid course name
    '''
    dept_name = desired_course.split()[0]
    if dept_name not in list(all_courses.keys()): #check department name
        return False
    if desired_course not in all_courses[dept_name]: #check number within the department
        return False
    
    return True
    
def course_error_message(course_error_name: str) -> None:
    '''
    Outputs an error if course name not found
    Parameter:
        course_error_name: a string of the course that is not found
    Return:
        None
    '''
    messagebox.showinfo('Info',f'{course_error_name} is not found \nPlease check formatting! Make sure to have a space between the department name and the course name!')

def empty_entries_error_message() -> None:
    '''
    Outputs an error message if no courses are entered from the user
    Parameters:
        None
    Return:
        None
    '''
    messagebox.showinfo('Info','Please enter a course!')

def end_program(window:tk) -> None:
    '''
    A function that closes a tk window or exits python if all windows are closed
    Parameter:
        window: the window that will be closed
    Return:
        None
    '''
    window.destroy()
    
def id_and_course_name_match(all_courses: dict, desired_courses: list):
    '''
    A function that creates a dictionary to match course ID to course name
    Parameters:
        all_courses: a dictionary containing all the departments, their respective courses, 
        the times within those respective courses and its corresponding IDs
        desired_courses: a list containing all the courses the user inputted
    Return:
        a dictionary containting all the IDs as keys and specific course names as values
    
    '''
    id_to_course_name = {} #initializes return dict
    sec_num_to_letter = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G'} #dict for converting section number to letters
    for course in desired_courses:
        dept = course.split()[0]
        course_info = all_courses[dept][course]
        if type(course_info) == dict: #check if it contains lab/discussion part
            for i, sections in enumerate(course_info['DL']): #lab part
                id_to_course_name[sections[1]] = f'{course} D/L{i+1}' #format lab course name
                
            for i, sections in enumerate(course_info['R']):
                if len(course_info) == 1:
                    section_title = f'{course}' #if there is only one section
                else:
                    section_title = f'{course} {sec_num_to_letter[i]}' #format regular course section name
                id_to_course_name[sections[1]] = section_title #append section title to appropriate ID number in dict
                
        else:   
            for i, sections in enumerate(course_info): #for non-lab sections
                if len(course_info) == 1:
                    section_title = f'{course}'
                else:
                    section_title = f'{course} {sec_num_to_letter[i]}'
                id_to_course_name[sections[1]] = section_title #append section title to appropriate ID number in dict
                
    return id_to_course_name 
    

def main(): 
    course_file = 'COURSE_DATA_ACTUAL.html'
    getDesireCourses(course_file)


if __name__ == "__main__":
    main()
