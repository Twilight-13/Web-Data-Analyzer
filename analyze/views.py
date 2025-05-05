import pandas as pd
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import io
import base64
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np  # Import numpy
import seaborn as sns  # Import seaborn


def analyze(request):
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            # Read the file, attempting different formats
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Error reading CSV: {e}")
                try:
                    df = pd.read_excel(file_path)
                except Exception as e:
                    print(f"Error reading Excel: {e}")
                    try:
                        df = pd.read_json(file_path)
                    except Exception as e:
                        print(f"Error reading JSON: {e}")
                        try:
                            df = pd.read_sql(file_path)  # This will likely fail, need a connection string
                        except Exception as e:
                            print(f"Error reading SQL: {e}")
                            return render(request, 'analyze.html', {
                                'error_message': 'Unsupported file format. Please upload a CSV, Excel, or JSON file.'
                            })

            # Data Analysis
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            shape = df.shape
            sample = df.head().to_html(index=False, classes='table table-striped table-bordered table-hover')
            info = df.info()  # Capture the output of df.info()
            describe = df.describe().to_html(classes='table table-striped table-bordered table-hover')

            # Missing Values Analysis
            missing_values = df.isnull().sum()
            has_missing_values = missing_values.any()
            if has_missing_values:
                missing_values_table = missing_values.to_frame(name='Missing Values').to_html(
                    classes='table table-striped table-bordered table-hover')
            else:
                missing_values_table = "No missing values"

            # Duplicates Analysis
            duplicated_count = df.duplicated().sum()
            has_duplicates = duplicated_count > 0

            # Correlation Analysis
            correlation_matrix_png = None
            correlation_matrix_error = None
            try:
                # Check if the DataFrame is empty
                if df.empty:
                    correlation_matrix_error = "Cannot calculate correlation matrix: DataFrame is empty."
                # Check if there are only non-numeric columns
                elif not any(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns):
                    correlation_matrix_error = "Cannot calculate correlation matrix: No numeric columns in the dataset."
                else:
                    # Select only numeric columns for correlation
                    numeric_df = df.select_dtypes(include=np.number)
                    if numeric_df.empty:
                        correlation_matrix_error = "No numeric columns available to calculate correlation."
                    else:
                        corr_matrix = numeric_df.corr()
                        plt.figure(figsize=(10, 8))
                        plt.imshow(corr_matrix, cmap='coolwarm', interpolation='none')
                        plt.colorbar()
                        plt.title('Correlation Matrix')
                        canvas = FigureCanvas(plt.gcf())
                        img_buffer = io.BytesIO()
                        canvas.print_png(img_buffer)
                        correlation_matrix_png = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        plt.close()
            except Exception as e:
                correlation_matrix_error = f"Error calculating correlation matrix: {e}"

            # Data Visualization
            plots = []
            plot_errors = []
            numeric_cols = df.select_dtypes(include='number').columns
            non_numeric_cols = df.select_dtypes(exclude='number').columns

            # Maximum plots to generate to prevent server overload
            MAX_PLOTS = 20  # Increased max plots
            MAX_UNIQUE_VALUES = 50  # Define maximum unique values for bar charts

            # Univariate Analysis
            for col in df.columns:
                try:
                    plt.figure()
                    if pd.api.types.is_numeric_dtype(df[col]):
                        sns.histplot(df[col], kde=True)
                        plt.title(f'Histogram of {col}')
                    else:
                        unique_value_count = df[col].nunique()
                        if unique_value_count <= MAX_UNIQUE_VALUES:
                            df[col].value_counts().plot(kind='bar')
                            plt.title(f'Bar Chart of {col}')
                        else:
                            plot_errors.append(
                                f"Skipping bar chart for {col}: too many unique values ({unique_value_count} > {MAX_UNIQUE_VALUES})"
                            )
                            plt.close()
                            continue  # Skip the rest of the loop for this column
                    canvas = FigureCanvas(plt.gcf())
                    img_buffer = io.BytesIO()
                    canvas.print_png(img_buffer)
                    plot_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                    plots.append(plot_img)
                    plt.close()
                except Exception as e:
                    plot_errors.append(f"Error generating plot for {col}: {e}")

            # Bivariate Analysis (Column to Column)
            for i, col1 in enumerate(df.columns):
                for j, col2 in enumerate(df.columns):
                    if i >= j:  # Avoid duplicate plots
                        continue
                    try:
                        plt.figure(figsize=(8, 6))
                        if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                            sns.scatterplot(x=col1, y=col2, data=df)
                            plt.title(f'Scatter Plot: {col1} vs {col2}')
                        elif pd.api.types.is_numeric_dtype(df[col1]) and not pd.api.types.is_numeric_dtype(df[col2]):
                            sns.boxplot(x=col2, y=col1, data=df)
                            plt.title(f'Box Plot: {col1} vs {col2}')
                        elif not pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                            sns.boxplot(x=col1, y=col2, data=df)
                            plt.title(f'Box Plot: {col2} vs {col1}')
                        else:  # Both categorical
                            unique_value_count1 = df[col1].nunique()
                            unique_value_count2 = df[col2].nunique()
                            if unique_value_count1 <= MAX_UNIQUE_VALUES and unique_value_count2 <= MAX_UNIQUE_VALUES:
                                ct = pd.crosstab(df[col1], df[col2])
                                ct.plot(kind='bar', stacked=True)
                                plt.title(f'Stacked Bar Chart: {col1} vs {col2}')
                            else:
                                plot_errors.append(
                                    f"Skipping plot for {col1} vs {col2}: too many unique values in one or both columns"
                                )
                                plt.close()
                                continue

                        canvas = FigureCanvas(plt.gcf())
                        img_buffer = io.BytesIO()
                        canvas.print_png(img_buffer)
                        plot_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        plots.append(plot_img)
                        plt.close()
                    except Exception as e:
                        plot_errors.append(f"Error generating plot for {col1} vs {col2}: {e}")

            # Facts Section
            facts = {}
            for col in df.columns:
                try:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        facts[col] = {
                            'max': df[col].max(),
                            'min': df[col].min(),
                            'most_common': df[col].mode().iloc[0],  # Handle multiple most common values
                            'data_type': str(df[col].dtype)
                        }
                    else:
                         facts[col] = {
                            'max': None,
                            'min': None,
                            'most_common': df[col].mode().iloc[0],  # Handle multiple most common values
                            'data_type': str(df[col].dtype)
                        }
                except Exception as e:
                    facts[col] = {
                            'max': None,
                            'min': None,
                            'most_common': None,  # Handle multiple most common values
                            'data_type': str(df[col].dtype)
                        }
                    plot_errors.append(f"Error generating facts for column {col} : {e}")

            context = {
                'results': {
                    'file_name': file_name,
                    'file_size': file_size,
                    'shape': shape,
                    'sample': sample,
                    'info': str(info),  # Convert info to string
                    'describe': describe,
                    'has_missing_values': has_missing_values,
                    'missing_values': missing_values_table,
                    'has_duplicates': duplicated_count,
                    'correlation_matrix_png': correlation_matrix_png,
                    'correlation_matrix_error': correlation_matrix_error,
                    'plots': plots,
                    'plot_errors': plot_errors,
                    'facts': facts,
                }
            }
            return render(request, 'analyze.html', context)
        except Exception as e:
            return render(request, 'analyze.html', {'error_message': f'Error processing file: {e}'})
    return render(request, 'analyze.html')  # Or redirect to home page if no file
