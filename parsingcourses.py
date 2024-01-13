#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 10:22:11 2023

@author: albertwang
"""

from bs4 import BeautifulSoup as bs4
import os


class CourseScheduler:
    '''
    The class takes in an .html file (schedule.html), parses through the HTML 
    and has a method that can return a formatted dictionary containing info
    that will be used to generate a schedule
    slots:
        _course_html: the .html file name in the folder
    '''
    __slots__ = ('_course_html')
    
    def __init__(self, _course_html: str) -> None:
        
        current_directory = os.getcwd() + f'/{_course_html}' #where the file is located
        with open(current_directory,'r') as file: #read it and pass the contents into beautiful soup for pasing
            read_file = file.read()
            all_courses = bs4(read_file, 'html.parser') 
        
        self._course_html = all_courses #put this bs4 object in the parsing instance variable
        
    def getAllCourses(self) -> dict:
        course_dict = {} #initializes return dict
        parse_courses = self._course_html
        departments = parse_courses.find_all('table', class_='datadisplaytable') #separate all the info for different departments
        departments_cleaned = [department.find_all('tr', class_= False) for department in departments] #clean out some of the unused data in each department
        date_conversion = {'M': 'MON', 'T': 'TUE', 'W':'WED','R':'THU','F':'FRI'} #dictionary for day conversion
        
        for department in departments_cleaned[:-1]: #loop through each department
            department_name = 'place_holder' #placeholder for department name
            courses = {} #initializes dictionary to hold course info in each department
            
            for i in range(2, len(department)): #loop through each course within a department
                course = department[i].find_all('td', class_='dddefault')
                department_name = department[2].find_all('td', class_='dddefault')[2].get_text() #the department name is in all of the first tds
                curr_department_name = course[2].get_text() #some tds needs to be filtered out 
                
                if curr_department_name != department_name: #check if a td has the correct department name
                    continue #end loop if not
                    
                course_name = f'{department_name} {course[3].get_text()}' #formatted course name
             
                course_day = course[8].get_text() #get days of the week (MTWRF)
                if course_day.isalpha() == False or course_day == 'TBA': #check if it's listed and in the correct format
                    converted_day = ['NA'] #if not, return 'NA'
                else:
                    converted_day = [date_conversion[course_day[i]] for i in range(len(course_day))] #if in correct format, convert format
                    
                course_time = course[9].get_text().upper().strip().split('-') #splits the time of course into [start time, end time]
                course_id = course[1].find('a').get_text() #get the course ID
                
                if converted_day != ['NA']: #check if there are listed days (no listed days indicates no listed time)
                    course_formatted_info = [[f'{day} {time}' #create a list of the start and end time on different days
                                             for time in course_time 
                                             for day in converted_day], course_id]
                else:
                    course_formatted_info = [converted_day, course_id] #returns 'NA' if no listed time
        
                if course_name in courses: #check if the course name is already in the dictionary
                    section = course[4].get_text() #if it is, check its section
                    letters_only = ''.join(char for char in section if char.isalpha()) #removes the integers in string
                    
                    if len(section) == 2 and len(letters_only) == 1 and (letters_only == 'L' or letters_only == 'D'): #ensures it's either L_i or D_i (not SL or just D)
                    
                        if type(courses[course_name]) == dict: #if discussion/lab is already created, add to the DL list
                            courses[course_name]['DL'].append(course_formatted_info)
                        else: #if not create a copy of the regular course section times (this will be completed by the time DL sections gets iterated)
                            temp_r_courses = courses[course_name] #copy of regular course section times
                            courses[course_name] = {'DL': [course_formatted_info], 'R': temp_r_courses} # intializes dictionary to contain DL sections and R sections
                    else:
                        courses[course_name].append(course_formatted_info) #if theres no lab, just add to the regular course section list
                else:
                    courses[course_name] = [course_formatted_info] #initializes the course and have it point to a section time

            course_dict[department_name] = courses #add all the courses in a department to a deparment (department name is the key)
        
        return course_dict #return course dict to generate schedule

def main():
    course_file = 'COURSE_DATA_ACTUAL.html'
    test = CourseScheduler(course_file)
    course_dict = test.getAllCourses()
    # print(course_dict)#test for looking at chem courses
    # print(course_dict)
    
if __name__ == '__main__':
    main()