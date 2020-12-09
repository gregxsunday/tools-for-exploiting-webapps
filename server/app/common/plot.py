from bokeh.models.sources import ColumnDataSource
from bokeh.models.glyphs import VBar
from bokeh.models import FactorRange, Range1d, LinearAxis, Grid
from bokeh.palettes import BuPu
from bokeh.plotting import figure


x_axis_legend = {
    "excepted": "Amount of request where exception occured during scan",
    "redirected": "Amount of responses with redirection status (3xx)",
    "status_400": "Amount of responses with status 4xx",
    "worked": "Amount of working requests",
    "mirrored_vuln": "Amount of responses with 'Access-Control-Allow-Origin: <mirrored_origin>'",
    "credentials_vuln": "Amount of responses with 'Access-Control-Allow-Credentials: true'"
}

tests_legend = {
    "Test_reflect_origin": "sending plain https://evil.com",
    "Test_prefix_domain": "sending the input domain as a evil.com subdomain",
    "Test_suffix_domain": "sending the input domain as a evil suffix",
    "Test_null": "sending null as origin",
    "Test_any_subdomain": "sending evil as subdomain for the input domain",
    "Test_http_trust": "sending the input domain using http protocol",
    "Test_special_characters": "including special character between the input domain and evil.com",
    "Test_dot_to_char": "changing dot in the input domain to the character \"A\""
}


def create_bar_chart(data, title, x_name, y_name, width=1200, height=300):
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=data[x_name])
    ydr = Range1d(start=0, end=max(data[y_name])*1.5)

    plot = figure(title=title, x_range=xdr, y_range=ydr)
    glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8)
    plot.add_glyph(source, glyph)

    xaxis = LinearAxis()
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

    return plot