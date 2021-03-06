# Smart-Data-Visualisation
Data visualization is the graphical representation of information and data. By using visual elements like charts, graphs, and maps, data visualization tools provide an accessible way to see and understand trends, outliers, and patterns in data.


It enables decision makers to see analytics presented visually, so they can grasp difficult concepts or identify new patterns. With interactive visualization, you can take the concept a step further by using technology to drill down into charts and graphs for more detail, interactively changing what data you see and how it’s processed.


If you’ve ever stared at a massive spreadsheet of data and couldn’t see a trend, you know how much more effective a visualization can be. The concept of using pictures to understand data has been around for centuries, from maps and graphs in the 17th century to the invention of the pie chart in the early 1800s.



A picture is worth a thousand words. A good visualization is worth a terabyte of data. Nowadays, the ability to create good visualizations has shifted from a nice-to-have skill to a must-have skill for all data analysts to help managers make business decisions, where data is the primary force behind for its high volume and overwhelming velocity. Despite the overwhelming choices of interactive data visualization tools for experts, non-experts have poor choices for effective visualization recommendation systems such that everyone can easily create great visualizations.


The current data visualization tools have allowed users to create good visualizations, only if the users know their data well. Ideally, the users need tools to automatically recommend visualizations, so they can simply pick the ones they like. This is hard, if not impossible, since among numerous issues, no consensus has emerged to quantify the goodness of a visualization that captures human perception.

So, I developed this model which takes a csv file which is to be visualized and associated meta-data of columns like column type, column name, column size etc as input and generates output in JSON format, predicting the type of chart that will best suite to represent your data.
