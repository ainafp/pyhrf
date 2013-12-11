

from numpy import *
#from scipy.stats import truncnorm, erfc
from scipy.stats import truncnorm
from scipy.special import erfc
from scipy.special import erf

class RandomGenerator():
    """B
    Abstract class to ensure the definition of the function generate.
    """
    def __call__(self, size):
        return self.generate(size)

    def generate(self, size):
        raise NotImplementedError

class GaussianGenerator(RandomGenerator):
    """
    Class encapsulating the gaussian random generator of numpy
    """
    def __init__(self, mean=0.0, var=1.0):
        self.mean = mean
        self.std = var**.5
        self.type = 'gaussian'
    
    def generate(self, size):
        return random.normal(self.mean, self.std, size)

class GammaGenerator(RandomGenerator):
    """
    Class encapsulating the gamma random generator of numpy
    """
    def __init__(self, mean=1.0, var=1.0):
        self.a = mean**2/(var+0.)
        self.b = var/(mean+0.)
        self.type = 'gamma'

    def generate(self, size):
        return random.gamma(self.a, self.b, size)

class BetaGenerator(RandomGenerator):
    """
    Class encapsulating the beta random generator of numpy
    """
    def __init__(self, mean=.5, var=0.1):
        frac = mean*(1. - mean)/var - 1
        self.a = mean * frac
        self.b = frac -self.a
        self.type = 'beta'

    def generate(self, size):
        return random.beta(self.a, self.b, size)

class LogNormalGenerator(RandomGenerator):
    """
    Class encapsulating the log normal generator of numpy
    """
    def __init__(self, meanLogN=1.0, varLogN=1.0):
        self.mean = log(meanLogN) - .5 * log( 1.+ varLogN/meanLogN**2) 
        self.std = sqrt( log( 1. + varLogN/meanLogN**2 ) )
        self.type = 'log-normal'

    def generate(self, size):
        return random.lognormal(self.mean, self.std, size)
    
class UniformGenerator(RandomGenerator):
    """
    Class encapsulating the random generator
    """
    def __init__(self, minV=0., maxV=1.0):
        self.minV = minV 
        self.maxV =maxV
        self.widthInterval = maxV -minV
        self.type = 'uniform'
    
    def generate(self, size):
        return self.widthInterval * random.rand(size) - + self.minV

class ZeroGenerator(RandomGenerator):
    """
    Class encapsulating the null distribution !!!!!!!!!
    """
    def __init__(self):
        self.type = 'zero-valued'
    
    def generate(self, size):
        return zeros(size, dtype=float)

class IndependentMixtureLaw:
    """
    Class handling the generation of values following an indenpendent mixture
    law. Requires the prior generator of label values. 
    """
    def __init__(self, states, generators):
        """
        Initialise an IndependentMixtureLaw instance i.e. a set of values
        generated by 'generators' according to the labels given in 'states' 
        """
        self.states = states
        nbc = self.states.getNbClasses()
        self.nbClasses = nbc
        self.generators = generators
        self.data = zeros(self.states.getSize(), dtype=float)
        self.generate()
        
    def generate(self):
        """
        Generate realisations of the mixture law.
        """
        for ic in xrange(self.states.getNbClasses()):
            labels = self.states.getFieldValues()
            m = where(labels==ic)
            cn = self.states.getClassName(ic)
            if cn != None:
                self.data[m] = self.generators[cn].generate(len(m[0]))
            #else a generator is not defined for this class, leave zeros



def rpnorm(n,m,s):
    """
    Random numbers from the positive normal distribution.
    rpnorm(n,m,s) is a vector of length n with random entries, generated
    from a positive normal distribution with mean m and standard
    deviation s.

    Original matlab code from:
    (c) Vincent Mazet, 06/2005
    Centre de Recherche en Automatique de Nancy, France
    vincent.mazet@cran.uhp-nancy.fr
    
    Reference:
    V. Mazet, D. Brie, J. Idier, 'Simulation of Positive Normal Variables
    using several Proposal Distributions', IEEE Workshop Statistical
    Signal Processing 2005, july 17-20 2005, Bordeaux, France.

    Adapted by Thomas VINCENT:
    thomas.vincent@cea.fr
    """

    if s<0:  Exception('Standard deviation must be positive.')
    if n<=0: Exception('n is wrong.')

    x = []

    nn = n

    #Intersections
    ca  = 1.136717791056118
    mA = (1-ca**2)/ca*s
    mC = s * sqrt(pi/2)
    
    while len(x)<nn:    
        if m < mA:     # 4. Exponential distribution
            a = (-m + sqrt(m**2+4*s**2)) / 2 / s**2
            z = -log(1-random.rand(n))/a
            rho = exp( -(z-m)**2/2/s**2 - a*(m-z+a*s**2/2) )

        elif m <= 0:   # 3. Normal distribution truncated at the mean
                       #  equality because 3 is faster to compute than the 2
            z = abs(random.randn(n))*s + m
            rho = (z>=0)

        elif m < mC:   # 2. Normal distribution coupled with the uniform one
            r = (random.rand(n) < m/(m+sqrt(pi/2)*s))
            u = random.rand(n)*m
            g = abs(random.randn(n)*s) + m
            z = r*u + (1-r)*g
            rho = r*exp(-(z-m)**2/2/s**2) + (1-r)*ones(n)

        else:          # 1. Normal distribution
            z = random.randn(n)*s + m
            rho = (z>=0)


        # Accept/reject the propositions
        reject = (random.rand(n) > rho)
        z = z[bitwise_not(reject)]
        if len(z)>0:
            x.extend(z)
        n = n-len(z)

    return array(x)



def truncRandn(size, mu=0., sigma=1., a=0., b=inf):

    if b == inf:
        return rpnorm(size, mu, sigmaC) + a
    else:
        tn = truncnorm(a, b, mu, sigma)
        return tn.rvs(size)


import numpy as np
from numpy.random import rand, randn

def gm_sample(means, variances, props, n=1):

    assert np.isscalar(n)
    assert len(means) == len(variances)
    assert len(props) == len(means)

    if not isinstance(means, np.ndarray):
        means = np.array(means)

    if not isinstance(variances, np.ndarray):
        variances = np.array(variances)


    labels = (rand(n)[:,np.newaxis] > np.cumsum(props)[np.newaxis,:]).sum(1)

    return randn(n) * variances[labels]**.5 + means[labels]
