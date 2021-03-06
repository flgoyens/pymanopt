import numpy as np
from numpy import linalg as la, random as rnd
from pymanopt.manifolds.manifold import Manifold
from pymanopt.manifolds.manifold import EuclideanEmbeddedSubmanifold


class Gaussian_Subspace(EuclideanEmbeddedSubmanifold):
    """
    This class is a class for the constraint Ax =b where A is random and
    full rank. I think the class does everything but needs to be tested
    """
    def __init__(self, A, b, n, s, Q=None):
        self._shape = [n, s]
        self.A = A
        self.b = b
        if Q is None:
            Q, _ = la.qr(A.T)
        self.Q = Q
        super().__init__('Random Gaussian subspace manifold', b.size)

    def proj(self, X, G):

        Y = G.reshape([np.prod(G.shape), 1])

        out = Y - self.Q@(self.Q.T@Y)
        # print("Av should be 0: "+str(la.norm(self.A@out)))
        return out.reshape(G.shape)
        # return (G - self.Q@(self.Q.T@G.reshape([1,
        # np.prod(G.shape)]))).reshape(G.shape)
        # TODO i think that I need to take G(:) and reshape the all thing
        # that I return

    def ehess2rhess(self, X, G, H, U):
        """Converts the Euclidean gradient `G` and Hessian `H` of a function at
        a point `X` along a tangent vector `U` to the Riemannian Hessian of `X`
        along `U` on the manifold. This uses the Weingarten map
        """
        return self.proj(X, H)

    def rand(self):  # random point on the manifold
        Y_ls, *_ = la.lstsq(self.A, self.b, rcond=None)
        vec = self.proj(Y_ls, rnd.randn(*self._shape))

        out = Y_ls.reshape(*self._shape) + vec
        return out

    def randvec(self, X):  # random vector in tangent space
        Y = self.proj(X, rnd.randn(*self._shape))
        return Y / self.norm(X, Y)

    @property
    def typicaldist(self):
        return np.sqrt(self.dim)

    def inner(self, X, G, H):
        return float(np.tensordot(G, H, axes=G.ndim))

    def norm(self, X, G):
        return la.norm(G)

    def dist(self, X, Y):
        return la.norm(X - Y)

    def exp(self, X, U):
        return X + U

    retr = exp

    def log(self, X, Y):
        return Y - X

    def transp(self, X1, X2, G):
        return G

    def pairmean(self, X, Y):
        return (X + Y) / 2

    def zerovec(self, X):
        return np.zeros(self._shape)


class Samples(EuclideanEmbeddedSubmanifold):
    """
    This is a class for matrix completion, the subspace is all the matrices
     that satisfy the observed entries.
     mask is a boolean array of the size of self
     samples is a vector (I think) with the values at the True entries
    """
    def __init__(self, mask, samples):
        self._shape = mask.shape
        self.mask = mask
        self.samples = samples
        super().__init__('Samples manifold', samples.size)

    def proj(self, X, G):
        # Can I MODIFY G LIKE THAT ? G should be passed by reference
        # see what other manifold classes do
        Y = G
        Y[self.mask] = 0
        return Y

    def ehess2rhess(self, X, G, H, U):
        """Converts the Euclidean gradient `G` and Hessian `H` of a function at
        a point `X` along a tangent vector `U` to the Riemannian Hessian of `X`
        along `U` on the manifold. This uses the Weingarten map
        """
        return self.proj(X, H)

    def rand(self):  # random point on the manifold
        # HERE WE NEED TO INITIALIZE INSIDE -1,
        Y = rnd.randn(*self._shape)
        # Y = lift.my_rescale(rnd.randn(*self._shape), 0.9)
        Y[self.mask] = self.samples
        return Y

    def make_feasible(self, X):
        # not sure at all how I am supposed to do this thing..
        X[self.mask] = self.samples
        return X

    def randvec(self, X):  # random vector in tangent space
        Y = self.proj(rnd.randn(*self._shape))
        return Y / self.norm(X, Y)

    @property
    def typicaldist(self):
        return np.sqrt(self.dim)

    def inner(self, X, G, H):
        return float(np.tensordot(G, H, axes=G.ndim))

    def norm(self, X, G):
        return la.norm(G)

    def dist(self, X, Y):
        return la.norm(X - Y)

    def exp(self, X, U):
        return X + U

    retr = exp

    def log(self, X, Y):
        return Y - X

    def transp(self, X1, X2, G):
        return G

    def pairmean(self, X, Y):
        return (X + Y) / 2

    def zerovec(self, X):
        return np.zeros(self._shape)
