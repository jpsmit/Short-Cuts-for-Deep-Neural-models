def convert_single_intp_to_html(string, intp, intp_ref=None):
    assert (len(string) == len(intp))
    raw_html = ''
    if intp_ref is None:
        intp_ref = intp
    for i, ir, w in zip(intp, intp_ref, string):

        if i > ir:  # false possitive
            color = '#fada5e'
        elif i < ir:  # false negative
            color = '#ff0000'
        elif i > 0:
            color = '#00ff00'
        else:
            color = '#ffffff'
        raw_html += '<span style=\'background:{color}\'> {w}</span>'.format(color=color, w=w)
    return raw_html


def convert_res_to_htmls(input_ids, pred_intp, gt_intp=None, tokenizer=None):
    token_list = tokenizer._convert_id_to_token(input_ids)
    pred_html = convert_single_intp_to_html(token_list, pred_intp, gt_intp)

    if gt_intp is not None:
        gt_html = convert_single_intp_to_html(token_list, gt_intp)
        return gt_html, pred_html
    else:
        return pred_html
