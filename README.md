# sat-comparison
The solver in python for resolution, DP and DPLL. 
Steps for using the script. 
run it in pycharm (or alternatives). 
follow the prompts on screen (i.e variable counts always should be 3 or above). 
clause range "y" for static variable count and dynamic (range from x to y) clause count. 
"n" for the inverse (static clauze dynamic variable). 
resolution can be turned off when asked if you want to run bigger sets of tests. 
the results are printed on the screen, but they will also be copied in benchmark_table.tex, its made to be directly used in latex papers. 
after running the program once, i recomend copypasting the contents of benchmark_table.tex in a txt.file as running the program again will change the results in benchmark_table.tex, no need to delete any information from this particular file is it gets overwritten from scratch on program run.

Graphs.py, this script is used in order to create latex graphs, it takes input from the input_data.txt where you will paste your benchmark table made by the main script, it is done this way in order to have the capacity to combine multiple tables into 1 graph. the output is split for each individual method, in order to copypaste them in the section corresponding to them in the graph
