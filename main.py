'''

Bokeh application for comparing free agents with signed players

Hendrix Hanes

'''

import pandas as pd
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Select, RangeSlider, Slider
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
cluster_df.set_index(["name","FA","position","rounded_age", "games", "cap"], inplace=True)
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
interactive_df['rounded_age'] = [str(x) for x in scaled_df.index.get_level_values("rounded_age")]
interactive_df['games'] = [str(x) for x in scaled_df.index.get_level_values("games")]
interactive_df['cap'] = [x for x in scaled_df.index.get_level_values("cap")]

datasource = ColumnDataSource(interactive_df)
color_mapping = factor_cmap(field_name="FA",palette=Category10_3,factors=interactive_df['FA'].unique())
position = Select(title="Position", value="All", options=["All","C","LW","RW","D"])
rounded_age = RangeSlider(start=17,end=45, step=1, value=(17,45), title="Age")
games = Slider(start=0,end=82,value=0,step=1,title="Min. GP")
cap = RangeSlider(start=0,end=13,value=(0,13),step=0.01,title="Cap Hit ($M)")
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
        <span style='font-size: 18px'>@name, @rounded_age, @position, @cap</span>
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
    size=15,
    legend_field="FA")
        

def update():
    if (position.value == "All"):
        selected = interactive_df
    else:
        selected = interactive_df[interactive_df.position == position.value]
    selected = selected[(pd.to_numeric(selected.rounded_age) >= rounded_age.value[0]) &
                        (pd.to_numeric(selected.rounded_age) <= rounded_age.value[1])]
    selected = selected[pd.to_numeric(selected.games) > games.value]
    selected = selected[(selected['cap'] == "UFA") | (selected['cap'] == "RFA") | 
                        ((selected['cap'].apply(lambda k: cap.value[0] if k in ["RFA","UFA"] else float(k[1:-1])) >= cap.value[0]) &
                        (selected['cap'].apply(lambda k: cap.value[0] if k in ["RFA","UFA"] else float(k[1:-1])) <= cap.value[1]))]
    datasource.data = dict(
        x=selected["x"],
        y=selected["y"],
        name=selected["name"],
        FA=selected["FA"],
        position=selected["position"],
        rounded_age=selected['rounded_age'],
        games=selected['games'],
        cap=selected['cap']
    )

controls = [position, rounded_age, games,cap]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
    
inputs = column(*controls, width=320)
l = column(row(inputs, plot_figure), sizing_mode="scale_both")

curdoc().title = "2021 Free Agents Comparisons"
curdoc().add_root(l)