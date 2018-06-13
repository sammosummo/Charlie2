import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import cmocean
from matplotlib import cm


cmap = cm.ScalarMappable(cmap=cmocean.cm.phase)
cmap.to_rgba([0., 0.5, 1.])


def make_item(c, f):
    theta = [0]
    clr = cmap.to_rgba(c)
    n = np.random.randint(4, 8)
    m = 2 * np.pi / n
    for j in range(n):
        a = (j * m) + (np.random.rand() * m)
        theta.append(a)
    theta.append(2 * np.pi)
    theta = np.array(theta) + np.random.uniform(0, 2 * np.pi)
    r = np.random.uniform(0, 1, len(theta))
    r[-1] = r[0]
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    tck, u = interpolate.splprep([x, y], s=0, t=1)
    unew = np.arange(0, 1.01, 0.01)
    out = interpolate.splev(unew, tck)
    fig, ax = plt.subplots(1, figsize=(1, 1))
    ax.plot(out[0], out[1], 'k', lw=2)
    ax.fill(out[0], out[1], c=clr)
    plt.tick_params(left=False, labelleft=False, right=False, bottom=False,
                    labelbottom=False)
    plt.box(False)
    plt.tight_layout(0)
    p = '/Users/smathias/Documents/Charlie2/charlie2/stimuli/visual/spatialmemory/'
    f = p + f
    plt.savefig(f, transparent=True)
    plt.close(fig)


for load in range(2, 22, 2):
    for trial in range(2):
        for item in range(load):
            c = np.random.uniform(0, 1)
            f = 'l%i_t%i_i%i.png' % (load, trial, item)
            make_item(c, f)
            if item >= load/2:
                if c > 0.5:
                    c-= 0.5
                else:
                    c+= 0.5
                f = 'l%i_t%i_i%i_r.png' % (load, trial, item)
                make_item(c, f)

