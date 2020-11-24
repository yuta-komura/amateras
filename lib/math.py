def round_down(num, digits: int):
    a = float(num)
    if digits < 0:
        b = 10 ** int(abs(digits))
        answer = int(a * b) / b
    else:
        b = 10 ** int(digits)
        answer = int(a / b) * b
    assert not(not(-0.01 < num < 0.01) and answer == 0)
    return answer
