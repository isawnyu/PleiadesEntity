def periodRanges(vocab):
    return {v['id']:(v['lower_bound'], v['upper_bound']) for v in vocab}


def temporal_overlap(a, b, period_ranges=None):
    """Compare two Temporal objects"""
    ra = a.temporalRange(period_ranges)
    rb = b.temporalRange(period_ranges)
    if not ra or not rb:
        return False
    else:
        amin, amax = ra
        bmin, bmax = rb
        return amin < bmax and amax > bmin or amin == bmin and amax == bmax


def to_ad(year):
    sign = (year > 0) * 2 - 1
    if sign >= 0:
        return "AD %d" % year
    else:
        return "%d BC" % (sign * year)
