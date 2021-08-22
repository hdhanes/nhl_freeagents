# nhl_freeagents
An unsupervised approach to comparisons between signed players and unestricted free agents in the NHL

## Approach

In this project, I wanted to provide a graphical comparison on the similarity between players in an easy-to-use Bokeh application, with an emphasis on available free agents. Using the filters on the side of the application, you can easy explore the league by position, cap hit, etc.

The data used for this project is available through the NHL API and Capfriendly. Baseline statistics, per 60 metrics and usage were used in conjunciton with the UMAP alogirthm for dimensinoality reduction in order to create the 2D plot. While this app does not include expected or possession data, this will be added in the future. Planned updates for this project are as follows:

    - Adding in expected and possession statistics
    - Clustering if applicable
    - Heat map with existing player rankings
    - Team highlighting/filter
    - Closest comparables per player
    - Auto update data
    - Player filter/search

## Getting Started

First, clone this repo onto your local computer.

Next, you will need some kind of virtual environment manager to properly set up an environment to run the application. Using conda, create a virtual envonrments from **requirements.txt**. You will also need to enable conda-forge as a channel. For example, if we were going to create an environment called nhl_freeagents:

```python
conda config --add channels conda-forge
conda create --name nhl_freeagents --file requirements.txt
```

After this, simply navigate to the ```nhl_freeagents``` directory and launch the bokeh app from your terminal:

```python
bokeh serve --show main.py
```
