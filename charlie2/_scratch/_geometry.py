import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import cmocean
from matplotlib import cm


cmap = cm.ScalarMappable(cmap=cmocean.cm.phase)
cmap.to_rgba([0., 0.5, 1.])


def make_item(c, f, n=None):
    theta = [0]
    clr = cmap.to_rgba(c)
    if not n:
        n = np.random.randint(3, 9)
    m = 2 * np.pi / n
    for j in range(n):
        a = (j * m) + (np.random.rand() * m)
        theta.append(a)
    theta.append(2 * np.pi)
    theta = np.array(theta) + np.random.uniform(0, 2 * np.pi)
    r = np.random.uniform(0.2, 1, len(theta))
    r[-1] = r[0]
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    tck, u = interpolate.splprep([x, y], s=0, t=1)
    unew = np.arange(0, 1.01, 0.01)
    out = interpolate.splev(unew, tck)

    theta = np.linspace(0, 2 * np.pi, 100)

    # the radius of the circle
    r = np.sqrt(0.6)

    # compute x1 and x2
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    fig, ax = plt.subplots(1, figsize=(1, 1))
    ax.plot(out[0], out[1], 'k', lw=2)
    ax.fill(out[0], out[1], c=clr)
    # ax.plot(x, y, "k", lw=2)
    # ax.fill(x, y, c=clr)

    plt.tick_params(
        left=False, labelleft=False, right=False, bottom=False, labelbottom=False
    )
    plt.box(False)
    plt.tight_layout(0)
    p = "/Users/sm2286/Documents/Projects/Charlie2/charlie2/stimuli/visual/visualmemory/"
    f = p + f
    plt.savefig(f, transparent=True)
    plt.close(fig)


if __name__ == '__main__':

    for load in [4]:
        for trial in range(30):
            # n_ = list(range(5, 12))
            # np.random.shuffle(n_)
            clrs = []
            for item in range(load):
                # if item == 0:
                #     clrs.append(np.random.uniform(0, 1))
                #     c = clrs[0]
                # else:
                #     while any(abs(c - c_) <= 0.01 for c_ in clrs):
                c = np.random.uniform(0, 1)
                # clrs.append(c)
                f = "l%i_t%i_i%i.png" % (load, trial, item)
                make_item(c, f)
                if item == 0:
                    if c > 0.5:
                        c -= 0.5
                    else:
                        c += 0.5
                    f = "l%i_t%i_i%i_r.png" % (load, trial, item)
                    make_item(c, f)
