'''

Bokeh application for comparing free agents with signed players

Hendrix Hanes

'''

from nhl_scraping.scraper import NHLSeasonScraper
import pandas as pd
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10_3
import umap
from bokeh.io import curdoc

#now we are going to scrape the data
try:
    #if sample data
    player_df = pd.read_csv("example_data/player_data.csv")
    player_df['FA'] = "Signed"
    fa_df = pd.read_csv("example_data/freeagent_data.csv")
    fa_df['FA'] = "Free Agent"
    print("Using example data...")
    
except:
    #if no sample data
    scraped = NHLSeasonScraper()
    scraped.scraperosters("2021")
    scraped.scrapeFA("2021")
    
    player_df = scraped.player_data
    player_df['FA'] = "Signed"
    fa_df = scraped.freeagent_data
    fa_df['FA'] = "Free Agent"
    print("Using scraped data...")
    
#now we are going to merge the datasets (no need for train test split)
cluster_frames = [player_df, fa_df]
cluster_df = pd.concat(cluster_frames)

#scale the data
scaler = StandardScaler()
cluster_df.set_index(["name","FA"], inplace=True)
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

datasource = ColumnDataSource(interactive_df)
color_mapping = factor_cmap(field_name="FA",palette=Category10_3,factors=interactive_df['FA'].unique())
plot_figure = figure(
    title='UMAP projection for comparing free agents with active players',
    plot_width=1000,
    plot_height=550,
    tools=('pan, wheel_zoom, reset')
)

plot_figure.add_tools(HoverTool(tooltips="""
<div>
    <div>
        <span style='font-size: 16px; color: #224499'>Name:</span>
        <span style='font-size: 18px'>@name</span>
    </div>
</div>
"""))

plot_figure.circle(
    'x',
    'y',
    source=datasource,
    color=color_mapping,
    line_alpha=0.6,
    fill_alpha=0.6,
    size=9,
    legend_field="FA")
curdoc().title = "2021 Free Agents Comparisons"
curdoc().add_root(plot_figure)
