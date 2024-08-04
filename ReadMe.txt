Installations needed
====================
a) Software applications:
   - python 3.9 or later: https://www.python.org/downloads/ (except for MYSQL the solution doesn't need any extra PIP packages)
	 download and run the installer with the default options
	 Note: (for Windows) ensure the option to include Python in the path is checked.
   - MySQL Ver 8.0.36: https://dev.mysql.com/downloads/mysql/ (for windows use the x86 x64 msi installer) just run the installer and use the default options
   - MySQL Community Workbench Ver 8.0

b) Python drivers for MYSQL andUnit Tests: 
Execute the following commands from a command prompt
	pip install mysql-connector-python
	pip install parameterized

Setting up the database
=======================
- Launch the MYSQL Community Workbench application
- From the database Menu, select connect to server (This will  come up automatically the first time) 
- Select local instance MyQLxx 
- It should then prompt you at some point to create a SysAdmin user and password. Note these user and password created as it will be needed to run the module
- From the toolbar icons strip select the option,Create New Schema (Note in MySQL world schema == database), choose a name and use the defaults to set it up.
- In the window, Schemas the new schema should appear in the list - right-click on it and select 'Set as default schema'.
- Open the CreateTables.sql in the solution (via file, open SQL script) 
- Execute the script by clicking on the Lightning Bolt icon.
  If there are no errors, in the output window (bottom centre of screen) about 7 or so lines of Green Dot icons will be displayed to indicate success. 
- In the Schema window, right-click on the Schema and select 'Refresh All'.
  Again if there are no errors, you should be able to expand tables and see all 7 tables, bus busstatus, chargepoint, etc 

Populating the database with initial Data
=========================================
Using MySQL  Workbench application 
- open LoadParameters.sql in the solution (via file, open SQL script) and execute it (by clicking on the Lightning Bolt icon).
  This will populate the buses and the charge points

  LoadParameters sets up the bus list and the charge points. this is typically only run once or is re-run if charge points or buses are added or removed.

- open LoadMoreEVs.sql in the solution (via file, open SQL script) and run it (lightning bolt icon).
  This will populate the  bus table, with 40 more EVs / buses 

  LoadMoreEVs sets up 40 more buses  in the database.  

  If there are no errors, a few lines with Green Dot Succcess icons will be displayed in the output window

In the schema window, Right-click on the Dchema and select 'Refresh All'.
if all is well you should be able to expand tables.
Right-click on each table (except charging schedule), select 'select top 1000 rows' and see actual data in the database.



Running the program
===================

- Ensure all the .py files and config.xml are in the same directory. 
- Open config.xml and ensure the database connection parameters match what you have set up in the previous steps 
  (This includes  the user credentials to allow the program to access the database schema.)
- From the command prompt execute the following command

		python EVScheduler.py 2023-12-01

The schdule will be output to the screen as well as in the Reports sub-diretory. 
 The output  should  resemble ExampleReport.txt
 

