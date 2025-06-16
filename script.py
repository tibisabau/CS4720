import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import numpy as np

file_paths = glob.glob("results/*.csv")
data_frames = []

for path in file_paths:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df['source_file'] = path

    if 'Project_Name' in df.columns and 'flaky?' in df.columns:
        df = df[df['Project_Name'].isin(['flapy_example', 'avwx-engine'])]
        df = df[df['flaky?'] != 'not flaky']
        data_frames.append(df)

combined_df = pd.concat(data_frames, ignore_index=True)

def plot_metric_by_test(combined_df, metric_column, output_filename="bar_chart.png", title=None):
    """
    Plots a bar chart showing the metric per test name, grouped by CSV file
    """
    if metric_column not in combined_df.columns:
        raise ValueError(f"Column '{metric_column}' not found in DataFrame.")

    plot_df = combined_df[['Test_name', metric_column, 'source_file']]
    plot_df = plot_df.groupby(['Test_name', 'source_file'])[metric_column].sum().reset_index()

    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=plot_df, x='Test_name', y=metric_column, hue='source_file')
    plt.title(title or f'{metric_column} per Test (by CSV File)')
    plt.xlabel('Test Name')
    plt.ylabel(f'{metric_column} Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()

# def plot_stacked_metric(combined_df, order_type='sameOrder', output_filename='stacked_plot.png', title=None):
#     """
#     Plots a stacked bar chart showing passed and failed test counts for each test name and source file
#     """
#     pass_col = f'Passed_{order_type}'
#     fail_col = f'Failed_{order_type}'

#     if pass_col not in combined_df.columns or fail_col not in combined_df.columns:
#         raise ValueError(f"Columns {pass_col} and/or {fail_col} not found in DataFrame.")

#     df_plot = combined_df[['Test_name', 'source_file', pass_col, fail_col]].copy()
#     df_plot = df_plot.groupby(['Test_name', 'source_file']).sum().reset_index()
#     df_melted = df_plot.melt(id_vars=['Test_name', 'source_file'], 
#                              value_vars=[pass_col, fail_col],
#                              var_name='Result', value_name='Count')

#     df_melted['Result'] = df_melted['Result'].str.replace(f'_{order_type}', '', regex=False)

#     df_melted['Legend'] = df_melted['source_file'] + ' - ' + df_melted['Result']

#     pivot_df = df_melted.pivot_table(index=['Test_name', 'source_file'], 
#                                      columns='Result', 
#                                      values='Count', 
#                                      fill_value=0).reset_index()

#     fig, ax = plt.subplots(figsize=(12, 6))
#     test_labels = pivot_df['Test_name'] + ' (' + pivot_df['source_file'] + ')'
#     ax.bar(test_labels, pivot_df['Passed'], label='Passed', color='green')
#     ax.bar(test_labels, pivot_df['Failed'], bottom=pivot_df['Passed'], label='Failed', color='red')

#     plt.xticks(rotation=45, ha='right')
#     plt.ylabel('Test Count')
#     plt.title(title or f'Test Outcomes ({order_type})')
#     plt.legend(title='Result')
#     plt.tight_layout()
#     plt.savefig(output_filename)
#     plt.close()

def plot_grouped_stacked_bar(combined_df, order_type='sameOrder', output_filename='grouped_stacked_plot.png', title=None):
    """
    Generates a grouped stacked bar chart with one group per Test_name
    Each group contains stacked bars per source_file with Passed and Failed
    """
    pass_col = f'Passed_{order_type}'
    fail_col = f'Failed_{order_type}'

    if pass_col not in combined_df.columns or fail_col not in combined_df.columns:
        raise ValueError(f"Columns {pass_col} and/or {fail_col} not found in DataFrame.")

    df_plot = combined_df[['Test_name', 'source_file', pass_col, fail_col]].copy()
    df_plot = df_plot.groupby(['Test_name', 'source_file']).sum().reset_index()

    df_plot = df_plot.sort_values(['Test_name', 'source_file'])

    test_names = df_plot['Test_name'].unique()
    source_files = df_plot['source_file'].unique()

    green_shades = ['#66c2a5', '#41ae76', '#238b45']  
    red_shades = ['#fc9272', '#fb6a4a', '#cb181d']   
    color_map = {}
    for i, src in enumerate(source_files):
        color_map[(src, 'Passed')] = green_shades[i % len(green_shades)]
        color_map[(src, 'Failed')] = red_shades[i % len(red_shades)]

    bar_width = 0.1
    x = np.arange(len(test_names))
    fig, ax = plt.subplots(figsize=(14, 6))

    for i, src in enumerate(source_files):
        src_data = df_plot[df_plot['source_file'] == src].set_index('Test_name')
        passed = [src_data.loc[test, pass_col] if test in src_data.index else 0 for test in test_names]
        failed = [src_data.loc[test, fail_col] if test in src_data.index else 0 for test in test_names]
        
        offset = (i - len(source_files)/2) * bar_width + bar_width/2
        positions = x + offset
        ax.bar(positions, passed, width=bar_width, color=color_map[(src, 'Passed')], label=f'{src} - Passed')
        ax.bar(positions, failed, width=bar_width, bottom=passed, color=color_map[(src, 'Failed')], label=f'{src} - Failed')

    ax.set_xticks(x)
    ax.set_xticklabels(test_names, rotation=45, ha='right')
    ax.set_ylabel('Test Count')
    ax.set_title(title or f'Passed and Failed ({order_type}) per Test and Source File')
    
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), title='Legend')

    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()


# plot_metric_by_test(combined_df, 'Passed_sameOrder', output_filename='passed_same_plot.png')
# plot_metric_by_test(combined_df, 'Passed_randomOrder', output_filename='passed_random_plot.png')
# plot_metric_by_test(combined_df, 'Failed_sameOrder', output_filename='failed_same_plot.png')
# plot_metric_by_test(combined_df, 'Failed_randomOrder', output_filename='failed_random_plot.png')

# plot_stacked_metric(combined_df, order_type='sameOrder', output_filename='stacked_same_order.png')
# plot_stacked_metric(combined_df, order_type='randomOrder', output_filename='stacked_random_order.png')

plot_grouped_stacked_bar(combined_df, order_type='sameOrder', output_filename='grouped_same_order.png')
plot_grouped_stacked_bar(combined_df, order_type='randomOrder', output_filename='grouped_random_order.png')


def plot_flakiness_bar_all_files(df, output_filename='flakiness_bar_all.png'):
    grouped = df.groupby(['source_file', 'flaky?']).size().reset_index(name='count')

    plt.figure(figsize=(12, 6))
    sns.barplot(data=grouped, x='source_file', y='count', hue='flaky?', palette='muted')
    plt.title('Flakiness Type Count per CSV File')
    plt.xlabel('Source File')
    plt.ylabel('Number of Tests')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()




def plot_flakiness_pie_all_files(df, output_filename='flakiness_pies_all.png'):
    grouped = df.groupby(['source_file', 'flaky?']).size().reset_index(name='count')
    source_files = grouped['source_file'].unique()
    num_files = len(source_files)

    cols = 3
    rows = (num_files + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten()  

    for i, source_file in enumerate(source_files):
        plot_data = grouped[grouped['source_file'] == source_file]
        axes[i].pie(
            plot_data['count'],
            labels=plot_data['flaky?'],
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette('muted')
        )
        axes[i].set_title(source_file)
        axes[i].axis('equal')

    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    fig.suptitle('Flakiness Distribution per File', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_filename)
    plt.close()


plot_flakiness_bar_all_files(combined_df)
plot_flakiness_pie_all_files(combined_df)


