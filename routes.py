# import re
# print('found routes')
# routes_in = ((r'.*/static/(?P<subdir>(css|images|audio|js))/(?P<basename>.*)\.[\d]{10}\.(?P<extension>(css|js|ico|png|svg|jpe?g|gif))',
#               r'/static/\g<subdir>/\g<basename>.\g<extension>'),
#              )
# print(re.match(routes_in[0][0],
#                '/static/css/theme.1510773357.css').groupdict())
# print(re.sub(routes_in[0][0],
#              routes_in[0][1], '/static/css/theme.1510773357.css'))
# routes_out = [(x, y) for (y, x) in routes_in]
