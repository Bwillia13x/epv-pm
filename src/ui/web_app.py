"""
Web Interface for EPV Research Platform
Interactive dashboard for stock analysis and EPV calculations
"""
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date
import logging

def create_app(platform):
    """Create and configure the Dash web application"""
    
    app = dash.Dash(__name__, title="EPV Research Platform")
    
    # Custom CSS
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("EPV Research Platform", 
                   style={'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '30px'}),
            html.P("Sophisticated Earnings Power Value Analysis & Intrinsic Value Calculator",
                  style={'textAlign': 'center', 'fontSize': '18px', 'color': '#7f8c8d'})
        ], style={'padding': '20px', 'backgroundColor': '#ecf0f1'}),
        
        # Main content
        html.Div([
            # Input section
            html.Div([
                html.H3("Stock Analysis", style={'color': '#2c3e50'}),
                
                # Stock symbol input
                html.Div([
                    html.Label("Stock Symbol:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='symbol-input',
                        type='text',
                        placeholder='Enter stock symbol (e.g., AAPL)',
                        style={'width': '100%', 'padding': '10px', 'margin': '5px 0'}
                    )
                ], style={'marginBottom': '15px'}),
                
                # Peer symbols input
                html.Div([
                    html.Label("Peer Symbols (optional):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='peers-input',
                        type='text',
                        placeholder='Enter peer symbols separated by commas (e.g., MSFT,GOOGL)',
                        style={'width': '100%', 'padding': '10px', 'margin': '5px 0'}
                    )
                ], style={'marginBottom': '15px'}),
                
                # Analysis type
                html.Div([
                    html.Label("Analysis Type:", style={'fontWeight': 'bold'}),
                    dcc.RadioItems(
                        id='analysis-type',
                        options=[
                            {'label': 'Quick EPV', 'value': 'quick'},
                            {'label': 'Full Analysis', 'value': 'full'}
                        ],
                        value='quick',
                        style={'margin': '10px 0'}
                    )
                ], style={'marginBottom': '15px'}),
                
                # Years selection
                html.Div([
                    html.Label("Years of Historical Data:", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id='years-slider',
                        min=3,
                        max=15,
                        value=10,
                        marks={i: str(i) for i in range(3, 16)},
                        step=1
                    )
                ], style={'marginBottom': '20px'}),
                
                # Analyze button
                html.Button(
                    'Analyze Stock',
                    id='analyze-button',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'padding': '12px 24px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px',
                        'width': '100%'
                    }
                ),
                
                # Loading indicator
                dcc.Loading(
                    id="loading-analysis",
                    type="default",
                    children=[html.Div(id="loading-output")]
                )
                
            ], style={
                'width': '30%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '20px',
                'backgroundColor': '#ffffff',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'margin': '10px'
            }),
            
            # Results section
            html.Div([
                html.Div(id='analysis-results')
            ], style={
                'width': '65%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '20px',
                'margin': '10px'
            })
            
        ], style={'padding': '20px'}),
        
        # Batch analysis section
        html.Div([
            html.H3("Batch Analysis", style={'color': '#2c3e50'}),
            
            html.Div([
                html.Label("Multiple Symbols (comma-separated):", style={'fontWeight': 'bold'}),
                dcc.Textarea(
                    id='batch-symbols-input',
                    placeholder='Enter multiple symbols separated by commas (e.g., AAPL,MSFT,GOOGL,AMZN)',
                    style={'width': '100%', 'height': '100px', 'padding': '10px', 'margin': '5px 0'}
                )
            ], style={'marginBottom': '15px'}),
            
            html.Button(
                'Run Batch Analysis',
                id='batch-analyze-button',
                n_clicks=0,
                style={
                    'backgroundColor': '#e74c3c',
                    'color': 'white',
                    'padding': '12px 24px',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'fontSize': '16px'
                }
            ),
            
            html.Div(id='batch-results', style={'marginTop': '20px'})
            
        ], style={
            'padding': '20px',
            'backgroundColor': '#ffffff',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'margin': '20px'
        })
        
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    
    # Callbacks
    @app.callback(
        Output('analysis-results', 'children'),
        Output('loading-output', 'children'),
        Input('analyze-button', 'n_clicks'),
        State('symbol-input', 'value'),
        State('peers-input', 'value'),
        State('analysis-type', 'value'),
        State('years-slider', 'value')
    )
    def analyze_stock(n_clicks, symbol, peers, analysis_type, years):
        if n_clicks == 0 or not symbol:
            return html.Div(), ""
        
        try:
            symbol = symbol.upper().strip()
            peer_symbols = None
            if peers:
                peer_symbols = [p.strip().upper() for p in peers.split(',') if p.strip()]
            
            if analysis_type == 'quick':
                results = platform.quick_epv(symbol)
                return create_quick_results_display(results), ""
            else:
                results = platform.analyze_stock(
                    symbol=symbol,
                    peer_symbols=peer_symbols,
                    years=years
                )
                return create_full_results_display(results), ""
                
        except Exception as e:
            error_message = html.Div([
                html.H4("Analysis Error", style={'color': '#e74c3c'}),
                html.P(f"Error analyzing {symbol}: {str(e)}", style={'color': '#c0392b'})
            ], style={
                'backgroundColor': '#fadbd8',
                'padding': '15px',
                'borderRadius': '4px',
                'border': '1px solid #e74c3c'
            })
            return error_message, ""
    
    @app.callback(
        Output('batch-results', 'children'),
        Input('batch-analyze-button', 'n_clicks'),
        State('batch-symbols-input', 'value')
    )
    def batch_analyze(n_clicks, symbols_text):
        if n_clicks == 0 or not symbols_text:
            return html.Div()
        
        try:
            symbols = [s.strip().upper() for s in symbols_text.split(',') if s.strip()]
            
            if not symbols:
                return html.Div("Please enter valid stock symbols", style={'color': '#e74c3c'})
            
            results = platform.batch_analysis(symbols, export_summary=False)
            return create_batch_results_display(results)
            
        except Exception as e:
            return html.Div(f"Batch analysis error: {str(e)}", style={'color': '#e74c3c'})
    
    return app

def create_quick_results_display(results):
    """Create display for quick EPV results"""
    
    # Key metrics cards
    metrics_cards = html.Div([
        # EPV Card
        html.Div([
            html.H4("EPV per Share", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"${results['epv_per_share']:.2f}", style={'color': '#27ae60', 'margin': '0'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Current Price Card
        html.Div([
            html.H4("Current Price", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"${results['current_price']:.2f}" if results['current_price'] else "N/A", 
                   style={'color': '#3498db', 'margin': '0'})
        ], style={
            'backgroundColor': '#d6eaf8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Margin of Safety Card
        html.Div([
            html.H4("Margin of Safety", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"{results['margin_of_safety']:.1f}%" if results['margin_of_safety'] is not None else "N/A",
                   style={
                       'color': '#27ae60' if results['margin_of_safety'] and results['margin_of_safety'] > 0 else '#e74c3c',
                       'margin': '0'
                   })
        ], style={
            'backgroundColor': '#d5f4e6' if results['margin_of_safety'] and results['margin_of_safety'] > 0 else '#fadbd8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Quality Score Card
        html.Div([
            html.H4("Quality Score", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"{results['quality_score']:.2f}", 
                   style={
                       'color': '#27ae60' if results['quality_score'] > 0.6 else '#f39c12' if results['quality_score'] > 0.4 else '#e74c3c',
                       'margin': '0'
                   })
        ], style={
            'backgroundColor': '#d5f4e6' if results['quality_score'] > 0.6 else '#fdeaa7' if results['quality_score'] > 0.4 else '#fadbd8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        })
    ], style={'marginBottom': '30px'})
    
    # Growth scenarios chart
    if results['growth_scenarios']:
        scenarios_df = pd.DataFrame([
            {'Scenario': scenario.replace('_', ' ').title(), 'Value': value}
            for scenario, value in results['growth_scenarios'].items()
        ])
        
        scenarios_chart = dcc.Graph(
            figure=px.bar(
                scenarios_df,
                x='Scenario',
                y='Value',
                title='EPV under Different Growth Scenarios',
                color='Value',
                color_continuous_scale='viridis'
            ).update_layout(
                xaxis_title="Growth Scenario",
                yaxis_title="Value per Share ($)",
                showlegend=False
            )
        )
    else:
        scenarios_chart = html.Div()
    
    # Summary info
    summary_info = html.Div([
        html.H3(f"Analysis Summary - {results['symbol']}", style={'color': '#2c3e50'}),
        html.P(f"Company: {results['company_name']}", style={'fontSize': '16px'}),
        html.P(f"Normalized Earnings: ${results['normalized_earnings']:,.0f}", style={'fontSize': '14px'}),
        html.P(f"Cost of Capital: {results['cost_of_capital']:.2%}", style={'fontSize': '14px'})
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '20px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '20px'
    })
    
    return html.Div([
        html.H3(f"Quick EPV Analysis - {results['symbol']}", style={'color': '#2c3e50'}),
        metrics_cards,
        summary_info,
        scenarios_chart
    ])

def create_full_results_display(results):
    """Create display for full analysis results"""
    
    # Key metrics (same as quick but with additional info)
    metrics_cards = html.Div([
        # EPV Card
        html.Div([
            html.H4("EPV per Share", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"${results['epv_per_share']:.2f}", style={'color': '#27ae60', 'margin': '0'}),
            html.P(f"Target: ${results['target_price']:.2f}" if results['target_price'] else "", 
                  style={'fontSize': '12px', 'margin': '5px 0 0 0'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Current Price Card
        html.Div([
            html.H4("Current Price", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"${results['current_price']:.2f}" if results['current_price'] else "N/A", 
                   style={'color': '#3498db', 'margin': '0'}),
            html.P(results['recommendation'], style={'fontSize': '12px', 'margin': '5px 0 0 0', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#d6eaf8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Margin of Safety Card
        html.Div([
            html.H4("Margin of Safety", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"{results['margin_of_safety']:.1f}%" if results['margin_of_safety'] is not None else "N/A",
                   style={
                       'color': '#27ae60' if results['margin_of_safety'] and results['margin_of_safety'] > 0 else '#e74c3c',
                       'margin': '0'
                   })
        ], style={
            'backgroundColor': '#d5f4e6' if results['margin_of_safety'] and results['margin_of_safety'] > 0 else '#fadbd8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Quality Score Card
        html.Div([
            html.H4("Quality Score", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"{results['quality_score']:.2f}", 
                   style={
                       'color': '#27ae60' if results['quality_score'] > 0.6 else '#f39c12' if results['quality_score'] > 0.4 else '#e74c3c',
                       'margin': '0'
                   })
        ], style={
            'backgroundColor': '#d5f4e6' if results['quality_score'] > 0.6 else '#fdeaa7' if results['quality_score'] > 0.4 else '#fadbd8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Risk Score Card
        html.Div([
            html.H4("Risk Score", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"{results['risk_score']:.2f}", 
                   style={
                       'color': '#27ae60' if results['risk_score'] < 0.4 else '#f39c12' if results['risk_score'] < 0.7 else '#e74c3c',
                       'margin': '0'
                   })
        ], style={
            'backgroundColor': '#d5f4e6' if results['risk_score'] < 0.4 else '#fdeaa7' if results['risk_score'] < 0.7 else '#fadbd8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        })
    ], style={'marginBottom': '30px'})
    
    # Investment thesis
    thesis_section = html.Div([
        html.H4("Investment Thesis", style={'color': '#2c3e50'}),
        html.P(results['investment_thesis'], style={'lineHeight': '1.6', 'fontSize': '15px'})
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '20px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '20px'
    })
    
    # Risk factors
    risk_section = html.Div([
        html.H4("Risk Factors", style={'color': '#2c3e50'}),
        html.Ul([html.Li(risk) for risk in results['risk_factors']])
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '20px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '20px'
    })
    
    return html.Div([
        html.H3(f"Full Analysis - {results['symbol']}", style={'color': '#2c3e50'}),
        metrics_cards,
        thesis_section,
        risk_section
    ])

def create_batch_results_display(results):
    """Create display for batch analysis results"""
    
    # Summary stats
    stats = results.get('summary_stats', {})
    summary_cards = html.Div([
        html.Div([
            html.H4("Analyzed", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(str(results['successful_analyses']), style={'color': '#3498db', 'margin': '0'})
        ], style={
            'backgroundColor': '#d6eaf8',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        html.Div([
            html.H4("Avg EPV", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(f"${stats.get('avg_epv', 0):.2f}", style={'color': '#27ae60', 'margin': '0'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        html.Div([
            html.H4("Undervalued", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(str(stats.get('undervalued_count', 0)), style={'color': '#27ae60', 'margin': '0'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        html.Div([
            html.H4("High Quality", style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.H2(str(stats.get('high_quality_count', 0)), style={'color': '#e67e22', 'margin': '0'})
        ], style={
            'backgroundColor': '#fdeaa7',
            'padding': '20px',
            'borderRadius': '8px',
            'textAlign': 'center',
            'width': '18%',
            'display': 'inline-block',
            'margin': '1%'
        })
    ], style={'marginBottom': '30px'})
    
    # Results table
    table_data = []
    for symbol, data in results['results'].items():
        if 'error' not in data:
            table_data.append({
                'Symbol': symbol,
                'Company': data['company_name'],
                'EPV': f"${data['epv_per_share']:.2f}",
                'Current Price': f"${data['current_price']:.2f}" if data['current_price'] else "N/A",
                'Margin of Safety': f"{data['margin_of_safety']:.1f}%" if data['margin_of_safety'] is not None else "N/A",
                'Quality Score': f"{data['quality_score']:.2f}",
                'Cost of Capital': f"{data['cost_of_capital']:.2%}"
            })
    
    results_table = dash_table.DataTable(
        data=table_data,
        columns=[
            {'name': 'Symbol', 'id': 'Symbol'},
            {'name': 'Company', 'id': 'Company'},
            {'name': 'EPV', 'id': 'EPV'},
            {'name': 'Current Price', 'id': 'Current Price'},
            {'name': 'Margin of Safety', 'id': 'Margin of Safety'},
            {'name': 'Quality Score', 'id': 'Quality Score'},
            {'name': 'Cost of Capital', 'id': 'Cost of Capital'}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        sort_action="native"
    )
    
    return html.Div([
        html.H3("Batch Analysis Results", style={'color': '#2c3e50'}),
        summary_cards,
        html.H4("Detailed Results", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        results_table
    ])
