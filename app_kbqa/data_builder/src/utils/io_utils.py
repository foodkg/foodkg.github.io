import json

def dump_json(data, file, indent=None):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=indent)
    except Exception as e:
        raise e

def load_json(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        raise e
    return data

def dump_ndjson(data, file):
    try:
        with open(file, 'w') as f:
            for each in data:
                f.write(json.dumps(each) + '\n')
    except Exception as e:
        raise e

def load_ndjson(file, return_type='array'):
    if return_type == 'array':
        return load_ndjson_to_array(file)
    elif return_type == 'dict':
        return load_ndjson_to_dict(file)
    else:
        raise RuntimeError('Unknown return_type: %s' % return_type)

def load_ndjson_to_array(file):
    data = []
    try:
        with open(file, 'r') as f:
            for line in f:
                data.append(json.loads(line.strip()))
    except Exception as e:
        raise e
    return data

def load_ndjson_to_dict(file):
    data = {}
    try:
        with open(file, 'r') as f:
            for line in f:
                data.update(json.loads(line.strip()))
    except Exception as e:
        raise e
    return data

def write_lines(path, data):
    with open(path, 'w') as fout:
        for each in data:
            fout.write('\t'.join(each) + '\n')
