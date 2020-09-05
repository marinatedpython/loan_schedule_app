import pandas as pd 
import pathlib
import dash
import dash_core_components as dcc 
import dash_html_components as html 
import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go 


app = dash.Dash(
	__name__,
	meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}]
)


app.layout = html.Div(
	[
		html.Div(
			[
				html.Div(
					[
						html.Img(
							src=app.get_asset_url('house.png'),
							id='house-image',
							style={
								'height': '60px',
								'width': 'auto',
								'margin-bottom': '25px'
							}
						)
					],
					className='one-third column'
				),
				html.Div(
					[
						html.Div(
							[
								html.H3(
									'LOAN CALCULATOR'
								)
							]
						)
					],
					className='one-half column',
					id='title'
				),
				html.Div(
					[
						html.A(
							html.Button(
								'Learn More',
								id='learn-more-button',
							),
							href='https://en.wikipedia.org/wiki/Amortization_schedule'
						)
					],
					className='one-third column',
					id='button'
				)
			],
			id='header',
			className='row flex-display',
			style={
				'margin-bottom': '25px'
			}
		),
		html.Div(
			[
				html.Div(
					[
						html.P(
							'Enter Principal Amount of the Loan:',
							className='control_label'
						),
						dcc.Input(
							type='number',
							style={
								'margin-left': '10px'
							},
							value=100000,
							id='principal',
							className='dcc_control'
						),
						html.P(
							'Enter Interest Rate Per Annum:',
							className='control_label'
						),
						dcc.Input(
							type='number',
							style={
								'margin-left': '10px'
						},
						value=0.05,
						id='interest_rate',
						className='dcc_control'
						),
						html.P(
							'Enter Length of the Loan in Years:',
							className='control_label'
						),
						dcc.Input(
							type='number',
							style={
								'margin-left': '10px'
							},
							value=20,
							id='loan_length',
							className='dcc_control'
						),
						html.P(
							'Select Repayment Frequency:',
							className='control_label'
						),
						dcc.Dropdown(
							id='repayment_frequency',
							options=[
								{'label': 'Monthly', 'value': 'Monthly'},
								{'label': 'Fortnightly', 'value': 'Fortnightly'},
								{'label': 'Weekly', 'value': 'Weekly'}
							],
							multi=False,
							style={
								'margin-left': '2px',
							},
							value='Monthly',
							className='dcc_control'
						)
					],
					className='pretty_container three columns',
				),
				html.Div(
					[
						html.Div(
							[
								dcc.Graph(
									id='amortization_graph'
								)
							],
							className='pretty_container'
						)
					],
					id='right-column',
					className='nine columns'
				)
			],
			className='row flex-display'
		),
		html.Div(
			[
				html.H6(
					'Loan Schedule:'
				),
				dash_table.DataTable(
					id='loan_schedule_table',
					style_table={
						'maxHeight': '300px',
						'overflowY': 'scroll'
					},
					style_cell={
						'width': '100px',
						'text-align': 'center'
					}
				)
			],
			className='pretty_container twelve columns'
		)
	]
)


def calculate_payment(principal, interest_rate, years, repayment_frequency):
	years_to_periods = {'Monthly': 12, 'Fortnightly': 26, 'Weekly': 52}
	IR = interest_rate / years_to_periods[repayment_frequency]
	return principal * ((IR * (1 + IR) ** (years * years_to_periods[repayment_frequency])) / ((1 + IR) ** (years * years_to_periods[repayment_frequency]) - 1))


def construct_loan_schedule(principal, interest_rate, years, repayment_frequency):
	years_to_periods = {'Monthly': 12, 'Fortnightly': 26, 'Weekly': 52}
	IR = interest_rate / years_to_periods[repayment_frequency]
	payment = calculate_payment(principal, interest_rate, years, repayment_frequency)
	build_schedule = [{'Period': 0, 'Interest': 0, 'Principal': 0, 'Balance': principal}]
	for i in range(years * years_to_periods[repayment_frequency]):
		build_schedule.append({'Period': i+1, 'Interest': round(IR * build_schedule[i]['Balance'], 2), 'Principal': round(payment - (IR * build_schedule[i]['Balance']), 2), 'Balance': round(build_schedule[i]['Balance'] - (payment - (IR * build_schedule[i]['Balance'])), 2)})
	return build_schedule


@app.callback(
	Output('amortization_graph', 'figure'),
	[
		Input('loan_schedule_table', 'data'),
		Input('loan_schedule_table', 'columns'),
		Input('repayment_frequency', 'value'),
		Input('loan_length', 'value')
	]
)
def update_graph(data, columns, repayment_frequency, years):
	df = pd.DataFrame(data, columns=['Period', 'Interest', 'Principal', 'Balance'])
	x_values = df['Period']
	y_values = df['Balance']
	data = [{'x': x_values, 'y': y_values}]
	layout = go.Layout(
		title=go.layout.Title(
			text='Loan Amortization Graph',
			xanchor='center'
		),
		xaxis=go.layout.XAxis(
			title=go.layout.xaxis.Title(
				text='Number of '+repayment_frequency+' Payment Periods'+' = '+str(years) + ' years'
			),
		),
		yaxis=go.layout.YAxis(
			title=go.layout.yaxis.Title(
				text='Loan Balance'
			)
		)
	)

	return {'data': data, 'layout': layout}


@app.callback(
	[
		Output('loan_schedule_table', 'data'),
		Output('loan_schedule_table', 'columns'),
	],
	[
		Input('principal', 'value'),
		Input('interest_rate', 'value'),
		Input('loan_length', 'value'),
		Input('repayment_frequency', 'value')
	]
)
def update_data_table(principal, interest_rate, years, repayment_frequency):
	# Have just put these conditionals in so that you can clear the inputs on debug mode. Dont need them if you turn debug=False.
	if principal == None:
		principal = 0
	if interest_rate == None or interest_rate == 0:
		interest_rate = 0.05
	if years == None or years == 0:
		years = 1
	if repayment_frequency == None:
		repayment_frequency = 'Monthly'
	data = construct_loan_schedule(principal, interest_rate, years, repayment_frequency)
	columns = [{'name': 'Period', 'id': 'Period'}, {'name': 'Interest', 'id': 'Interest'}, {'name': 'Principal', 'id': 'Principal'}, {'name': 'Balance', 'id': 'Balance'}]
	return data, columns


if __name__ == '__main__':
	app.run_server(debug=True)
