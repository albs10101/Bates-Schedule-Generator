Goal and Scope

Students at Bates, especially those handling heavy course loads, often face challenges when choosing courses with non-overlapping schedules.
In response, we developed and tested an application to assist students in easily identifying compatible course combinations. For example, if a 
student wishes to take PHYS 109, CHEM 108A, ECON 255, and PHYS 458 simultaneously, the application generates 18 different schedule combinations. 
The optimization algorithm begins with a single course, checking for conflicts between its sections and labs with those of a second course. 
If conflicts arise, such as between sections of different courses or between a section of one course and a lab of another, the algorithm eliminates 
the problematic combinations. When adding a third course, its sections and labs are compared only to combinations that worked for the first two courses. 
If no compatible combinations are found for the entered courses, the user receives a blank schedule.

The application comprises two Python files. The first, parsingcourses.py, includes the CourseScheduler class, parsing the "ACTUAL_COURSE_DATA.html" file to create 
a course catalog dictionary. The second file, schedule_generator.py, contains functions controlling the tkinter user interface and optimization functions for the 
scheduling process. For potential project expansions, we might consider directly pulling the .html file from Garnet Gateway using requests, allowing users to access 
schedules from different semesters easily. Additionally, we could enable students to specify a time interval for scheduling courses. The current code also needs to address
cases where courses with labs list the lab under the same CRN (e.g., CHEM 215). To solve this problem, I would need to adapt the CourseScheduler's output dictionary to 
combine class and lab times into a single time list for single lab time cases.
