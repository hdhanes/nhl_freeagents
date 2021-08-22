'''

Bokeh application for comparing free agents with signed players

Hendrix Hanes

'''

import pandas as pd
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Select
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10_3
import umap
from bokeh.io import curdoc
from bokeh.layouts import column, row

#use currently scraped data (stored in current_data)
player_df = pd.read_csv("current_data/player_data.csv")
player_df['FA'] = "Signed"
fa_df = pd.read_csv("current_data/freeagent_data.csv")
fa_df['FA'] = "Free Agent"  
    
#now we are going to merge the datasets (no need for train test split)
cluster_frames = [player_df, fa_df]
cluster_df = pd.concat(cluster_frames)

#scale the data
scaler = StandardScaler()
cluster_df.set_index(["name","FA","position"], inplace=True)
cluster_df.drop("id",axis=1,inplace=True)
scaled_df = pd.DataFrame(scaler.fit_transform(cluster_df))
scaled_df.columns = cluster_df.columns
scaled_df.index = cluster_df.index

#umap clustering
embedding = umap.UMAP(random_state=42).fit_transform(scaled_df)

#now bokeh plotting the closest comparables
interactive_df = pd.DataFrame(embedding, columns=('x', 'y'))
interactive_df['FA'] = [str(x) for x in scaled_df.index.get_level_values("FA")]
interactive_df['name'] = [x for x in scaled_df.index.get_level_values("name")]
interactive_df['position'] = [x for x in scaled_df.index.get_level_values("position")]

datasource = ColumnDataSource(interactive_df)
color_mapping = factor_cmap(field_name="FA",palette=Category10_3,factors=interactive_df['FA'].unique())
position = Select(title="Position", value="All", options=["All","C","LW","RW","D"])
plot_figure = figure(
    title='UMAP projection for comparing free agents with active players',
    plot_width=1000,
    plot_height=550,
    sizing_mode="scale_both",
    tools=('pan, wheel_zoom, reset')
)

plot_figure.add_tools(HoverTool(tooltips="""
<div>
    <div>
        <span style='font-size: 16px; color: #224499'>Player:</span>
        <span style='font-size: 18px'>@name, @position</span>
    </div>
</div>
"""))

plot_figure.scatter(
    'x',
    'y',
    source=datasource,
    color=color_mapping,
    line_alpha=0.6,
    fill_alpha=0.6,
    size=9,
    legend_field="FA")

def update():
    if (position.value == "All"):
        selected = interactive_df
    else:
        selected = interactive_df[interactive_df.position == position.value]
    datasource.data = dict(
        x=selected["x"],
        y=selected["y"],
        name=selected["name"],
        FA=selected["FA"],
        position=selected["position"]
    )

controls = [position]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
    
inputs = column(*controls, width=320)
l = column(row(inputs, plot_figure), sizing_mode="scale_both")

curdoc().title = "2021 Free Agents Comparisons"
curdoc().add_root(l)