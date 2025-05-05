# Data Analysis Web Application

This web application allows users to upload a file (CSV, Excel, or JSON) and perform basic data analysis. The analysis includes:

* File information (name, size, shape)
* Sample data
* Column information (data types)
* Descriptive statistics
* Missing values analysis
* Duplicates analysis
* Correlation matrix
* Data visualization (histograms, bar charts, scatter plots, box plots)
* Column facts (max, min, most common value, data type)

## Features

* **File Upload:** Upload data files in CSV, Excel, or JSON formats.
* **Data Analysis:** Automatically performs a suite of data analysis tasks.
* **Results Display:** Presents the analysis results in a clear and organized web page.
* **Data Visualization:** Generates various plots to help visualize the data.
* **Error Handling:** Provides informative error messages for unsupported file formats or processing issues.

## Technologies Used

* Python
* Django
* Pandas
* Matplotlib
* Seaborn
* HTML
* CSS
* Tailwind CSS
* JavaScript

## How to Use

1.  Upload a data file (CSV, Excel, or JSON) using the file upload form.
2.  The application will automatically analyze the data and display the results on the page.
3.  The results include file information, sample data, column statistics, missing value analysis, plots, and column facts.

## Code Structure

* `analyze/views.py`: Contains the Django view function (`analyze`) that handles file uploads, performs data analysis using Pandas, and generates plots using Matplotlib and Seaborn.
* `analyze/urls.py`: Defines the URL pattern for the analyze view.
* `analyze/templates/analyze.html`: The HTML template used to display the analysis results.
* `requirements.txt`: Lists the Python dependencies for the project.

## Future Improvements

* Add more data visualization options.
* Implement more advanced data analysis techniques.
* Allow users to select specific columns for analysis.
* Improve the user interface and add more interactive elements.
* Add support for larger file sizes.
* Implement user authentication.
* Add ability to save analysis results.
* Implement background task processing for long running tasks.

## Contributions

Contributions are welcome! If you find any bugs or have suggestions for new features, please feel free to open an issue or submit a pull request.

## License
