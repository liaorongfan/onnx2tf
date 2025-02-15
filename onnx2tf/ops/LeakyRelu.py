import random
random.seed(0)
import numpy as np
np.random.seed(0)
import tensorflow as tf
import onnx_graphsurgeon as gs
from onnx2tf.utils.common_functions import (
    get_constant_or_variable,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
)


@print_node_info
@inverted_operation_enable_disable
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """LeakyRelu

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    before_op_output_shape_trans_1 = \
        tf_layers_dict.get(graph_node.inputs[0].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans = \
        before_op_output_shape_trans_1

    graph_node_input = get_constant_or_variable(
        graph_node.inputs[0],
        before_op_output_shape_trans,
    )
    graph_node_output: gs.Variable = graph_node.outputs[0]
    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    alpha = graph_node.attrs.get('alpha', 0.01)
    replace_leakyrelu_to_pseudo_leakyrelu = \
        kwargs['replace_leakyrelu_to_pseudo_leakyrelu']

    # Preserving Graph Structure (Dict)
    tf_layers_dict[graph_node_output.name] = {
        'optype': graph_node.op,
        'shape': shape,
        'dtype': dtype,
    }

    input_tensor = tf_layers_dict[graph_node_input.name]['tf_node'] \
        if isinstance(graph_node_input, gs.Variable) else graph_node_input

    # Generation of TF OP
    tf_op_type = None
    if not replace_leakyrelu_to_pseudo_leakyrelu:
        tf_layers_dict[graph_node_output.name]['tf_node'] = \
            tf.nn.leaky_relu(
                features=input_tensor,
                alpha=alpha,
                name=graph_node.name,
            )
        tf_op_type = tf.nn.leaky_relu
    else:
        tf_layers_dict[graph_node_output.name]['tf_node'] = \
            tf.maximum(0.0, input_tensor) + \
                tf.minimum(0.0, alpha * input_tensor)
        tf_op_type = 'tf.maximum + tf.minimum'

    # Generation of Debug Info
    tf_layers_dict[graph_node_output.name]['tf_node_info'] = \
        make_tf_node_info(
            node_info={
                'tf_op_type': tf_op_type,
                'tf_inputs': {
                    'features': input_tensor,
                    'alpha': alpha,
                },
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
