def check_config(config):
    if 'topN' in config:
        if not isinstance(config['topN'], int):
            config['topN'] = 10
            print("Invalid configuration value for topN. \
                Set to %s (default)." % config['topN'])
    else:
        config['topN'] = 10

    if 'titleAnalyzer' in config:
        if not isinstance(config['topN'], dict):
            config['titleAnalyzer'] = {'lowercase': True,
                                       'stemming': True,
                                       'stopwords': True}
            print("Invalid configuration value for titleAnalyzer. \
                Set to %s (default)." % config['titleAnalyzer'])
    else:
        config['titleAnalyzer'] = {'lowercase': True,
                                   'stemming': True,
                                   'stopwords': True}
    return config
