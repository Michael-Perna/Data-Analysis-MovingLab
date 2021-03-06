import numpy as np
import math
from . import ellipsoid


def deg_to_dms(deg, type='lat'):
    decimals, number = math.modf(deg)
    d = int(number)
    m = int(decimals * 60.0)
    s = (deg - d - m / 60.0) * 3600.00
    compass = {'lat': ('N', 'S'), 'lon': ('E', 'W')}
    compass_str = compass[type][0 if d >= 0 else 1]
    return '{} {} {:.6f} {}'.format(abs(d), abs(m), abs(s), compass_str)


def llh2xyz(llh, datum):
    # Lambda, Phi, Height
    # Ellipsoidal to geocentric
    lamb = llh[0]
    phi = llh[1]
    h = llh[2]

    a = ellipsoid.ell[ellipsoid.ell_index[datum]][0]
    b = ellipsoid.ell[ellipsoid.ell_index[datum]][1]
    e2 = ellipsoid.ell[ellipsoid.ell_index[datum]][3]
    Rn = a / np.sqrt(1.0-e2*np.sin(phi)**2)
    X = (Rn+h)*np.cos(phi)*np.cos(lamb)
    Y = (Rn+h)*np.cos(phi)*np.sin(lamb)
    Z = (Rn*(1.0-e2)+h)*np.sin(phi)

    return [X, Y, Z]


def lv95_projection(llh):
    lamb = llh[0]
    phi = llh[1]
    h = llh[2]

    # constants
    a = 6377397.155  # m
    E2 = 0.006674372230614  # m
    phi0 = np.pi/180.0*(46.0+57.0/60.0+8.66/3600.0)
    lambda0 = np.pi/180.0*(7.0+26.0/60.0+22.50/3600.0)

    # Derived constants
    R = (a*np.sqrt(1.0-E2))/(1.0-E2*np.sin(phi0)**2)
    alpha = np.sqrt(1.0+(E2/(1.0-E2))*(np.cos(phi0)**4))
    b0 = np.arcsin(np.sin(phi0)/alpha)

    # Calculus
    E = np.sqrt(E2)
    K = np.log(np.tan(np.pi / 4.0 + b0 / 2.0)) - alpha * np.log(
        np.tan(np.pi / 4.0 + phi0 / 2.0)) + alpha * E / 2.0 * np.log(
        (1.0 + E * np.sin(phi0)) / (1.0 - E * np.sin(phi0)))

    S = alpha*np.log(np.tan(np.pi / 4.0 + phi / 2.0)) - (alpha*E/2.0) * \
        np.log((1.0+E*np.sin(phi))/(1.0-E*np.sin(phi))) + K
    b = 2.0*(np.arctan(np.power(np.e, S))-np.pi/4.0)

    l = alpha*(lamb - lambda0)

    # equator system
    l_mean = np.arctan(np.sin(l)/(np.sin(b0)*np.tan(b)+np.cos(b0)*np.cos(l)))
    b_mean = np.arcsin(np.cos(b0)*np.sin(b)-np.sin(b0)*np.cos(b)*np.cos(l))

    Y = R*l_mean + 2600000.0
    X = R/2.0 * np.log((1.0+np.sin(b_mean))/(1.0-np.sin(b_mean))) + 1200000.0

    ENH = [Y, X, h]
    return ENH


def inverse_lv95_projection(enh):
    ELV95 = enh[0]
    NLV95 = enh[1]
    h_ell = enh[2]

    # constants
    a = 6377397.155  # m
    E2 = 0.006674372230614  # m
    phi0 = np.pi/180.0*(46.0+57.0/60.0+8.66/3600.0)
    lambda0 = np.pi/180.0*(7.0+26.0/60.0+22.50/3600.0)

    # Derived constants
    R = (a*np.sqrt(1.0-E2))/(1.0-E2*np.sin(phi0)**2)
    alpha = np.sqrt(1.0+(E2/(1.0-E2))*(np.cos(phi0)**4))
    b0 = np.arcsin(np.sin(phi0)/alpha)

    # Calculus
    E = np.sqrt(E2)
    K = np.log(np.tan(np.pi/4.0+b0/2.0))-alpha*np.log(np.tan(np.pi/4.0+phi0/2.0)
                                                      )+alpha*E/2.0*np.log((1.0+E*np.sin(phi0))/(1.0-E*np.sin(phi0)))

    Y = ELV95 - 2600000
    X = NLV95 - 1200000

    l_mean = Y/R
    b_mean = 2.0*(np.arctan(np.exp(X/R))-np.pi/4.0)

    b = np.arcsin(np.cos(b0)*np.sin(b_mean) + np.sin(b0)
                  * np.cos(b_mean)*np.cos(l_mean))
    l = np.arctan((np.sin(l_mean))/(np.cos(b0) *
                  np.cos(l_mean)-np.sin(b0)*np.tan(b_mean)))

    lamb = lambda0 + l/alpha

    # approx
    phi = b

    for i in range(10):
        # iterative part
        S = (1.0/alpha)*(np.log(np.tan(np.pi/4.0+b/2.0))-K)+E * \
            np.log(np.tan(np.pi/4.0+np.arcsin(E*np.sin(phi))/2.0))
        phi = 2.0*np.arctan(np.exp(S))-np.pi/2

    return [lamb, phi, h_ell]


def ch2etrs(xyz):
    X = xyz[0] + 674.374
    Y = xyz[1] + 15.056
    Z = xyz[2] + 405.346

    return [X, Y, Z]


def etrs2ch(xyz):
    X = xyz[0] - 674.374
    Y = xyz[1] - 15.056
    Z = xyz[2] - 405.346

    return [X, Y, Z]


def itrf2ch(xyz, drift):
    X = xyz[0] + drift[0]  # 0.4922
    Y = xyz[1] + drift[1]  # 0.5092
    Z = xyz[2] + drift[2]  # 0.3821

    return [X, Y, Z]


def xyz2llh(xyz, datum):
    #  Reprojection
    a = ellipsoid.ell[ellipsoid.ell_index[datum]][0]
    e2 = ellipsoid.ell[ellipsoid.ell_index[datum]][3]

    XETRS = xyz[0]
    YETRS = xyz[1]
    ZETRS = xyz[2]

    p = np.sqrt(XETRS**2+YETRS**2)
    phi_global = np.arctan(ZETRS/((1.0-e2)*p))
    lamb_global = np.arctan(YETRS/XETRS)
    h_global = 0
    for i in range(20):
        Rn = a / np.sqrt(1.0-e2*np.sin(phi_global)**2)
        phi_global = np.arctan(ZETRS/(p*(1.0-e2*(Rn)/(Rn+h_global))))
        h_global = p/np.cos(phi_global)-Rn

    return [lamb_global, phi_global, h_global]


def lv95_to_wgs84(enh):
    llh = inverse_lv95_projection(enh)
    xyz = llh2xyz(llh, "Bessel1841")
    xyz = ch2etrs(xyz)
    llh = xyz2llh(xyz, "WGS84")

    llh[0] = 180 / np.pi * llh[0]
    llh[1] = 180 / np.pi * llh[1]

    return llh


def wgs84_to_lv95(llh):
    llh[0] = np.pi / 180 * llh[0]
    llh[1] = np.pi / 180 * llh[1]

    xyz = llh2xyz(llh, "WGS84")
    xyz = etrs2ch(xyz)
    llh = xyz2llh(xyz, "Bessel1841")
    enh = lv95_projection(llh)
    return enh


def wgs84_itrf14_to_lv95(llh, drift):
    llh[0] = np.pi / 180 * llh[0]
    llh[1] = np.pi / 180 * llh[1]

    xyz = llh2xyz(llh, "WGS84")
    xyz = etrs2ch(xyz)
    xyz = itrf2ch(xyz, drift)
    llh = xyz2llh(xyz, "Bessel1841")
    enh = lv95_projection(llh)
    return enh
