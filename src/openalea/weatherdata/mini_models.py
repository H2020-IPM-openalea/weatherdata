""" Short meteorological models """

def temp_par(self, Tair, PAR):
    """ Return an estimation of air temperature near the leaf
    
    :Parameters:
    ------------
    - 'Tair' (float)
        Temperature above the canopy (in degrees celsius)
    - 'PAR' (float)
        Photosynthetic Active Radiation (ppfd in micromol.m-2.sec-1)
        
    :Returns:
    ---------
    - 'Tair_leaf' (float)
        Temperature of the air around the leaf (in degrees celsius)
    """
    Tair_leaf = Tair + (PAR / 300)
    return Tair_leaf
    
def leaf_wetness_rapilly(rain_intensity=0., relative_humidity=0., PPFD=0.):
    """ Compute leaf wetness as in Rapilly et Jolivet, 1976 as a 
        function of rain or relative humidity and PAR.
    
    Parameters
    ----------
    rain_intensity: float
        Rain (in mm.h-1)
    relative_humidity: float
        Relative humidity of the air around the leaf (in %)
    PPFD: float
        Photosynthetically active radiation around the leaf (in nm)
    
    Returns
    -------
    wet: True or False
        True if the leaf is wet
    """
    if rain_intensity>0. or (relative_humidity >= 85. and PPFD < 644.):
        return True
    else:
        return False

def leaf_wetness_pedro_gillepsie(leaf_geometry=None, rain_intensity=0., temperature_air=0., 
                                 wind_speed=0., wind_direction=(0.,0.,0.), 
                                 relative_humidity=0., net_radiation=0.):
    """ Calculate the presence/absence of free water on the surface of a given leaf.
    
    For a given time step, leaf is wet if rain is intercepted. The model uses the
    equations from the following article to calculate presence/absence of dew:
    Estimating dew duration. I. Utilizing micrometeorological data
    Agricultural Meteorology, Volume 25, 1981, Pages 283-296
    M.J. Pedro Jr., T.J. Gillespie
    
    link: http://www.sciencedirect.com/science/article/pii/0002157181900819

    Parameters
    ----------
    leaf_geometry: OpenAlea plantgl shape
        Geometry of the chosen
    rain_intensity: float
        Rain intensity on leaf (mm/unit of time step)
    temperature_air: float
        Temperature of the air around the leaf (in degrees celsius)
    wind_speed: float
        Wind speed at leaf height (in m.s-1)
    wind_direction: tuple(x,y,z)
        Vector of wind direction
    relative_humidity: float
        Relative humidity around the leaf (in %)
    net_radiation: float
        Net radiation perceived by the leaf (in W.m-2)
        
    Returns
    -------
    True or False:
        True if leaf is wet
    """
    
    def calculate_hc(leaf_geometry=None, wind_speed=0., wind_direction=(0.,0.,0.)):
        """ Calculate the convective heat transfer coefficient.
        
        Returns
        -------
        hc: float
            Convective heat transfer coefficient (in W.m-2.degrees celsius-1)
            
        ..TODO:: take into account leaf geometry and wind direction to calculate D
        """
        # Width of the leaf in wind direction (in cm):
        D = 10.
        # TODO : take into account leaf geometry and wind direction to calculate D
        return 40*(wind_speed/D)**0.5
        
    def calculate_hw(hc=0.):
        """ Calculate the water vapour transfer coefficient.
        
        Parameters
        ----------
        hc: float
            Convective heat transfer coefficient (in W.m-2.degrees celsius-1)
        
        Returns
        -------
        hw: float
            Water vapour transfer coefficient (in W.m-2)
        """
        # Latent heat of vaporization of water (in J.kg-1)
        L = 2260*10**3
        # Specific heat of the air (in J.kg-1.degrees celsius-1)
        Cp = 1006
        return hc*1.07*L/Cp
    
    def calculate_psat(T):
        """ Calculate the saturation water vapour pressure at temperature T.
        
        Returns
        -------
        es: float
            Saturation water vapour pressure (in mbar)
        """
        return 611.*10**(7.5*T/(237.2+T));
    
    def calculate_p(es=0., relative_humidity=0.):
        """ Calculate the ambient water vapour pressure.
        
        Returns
        -------
        e: float
            Ambient vapour pressure (in mbar)
        """
        return es*relative_humidity/100.
    
    def calculate_slope(T):
        """ Calculate slope of the saturation vapour pressure curve at T.
        
        Returns
        -------
        s: float
            Slope of the saturation vapour pressure curve at T (in mbar.degrees celsius-1)
        """
        return (2.50389*10**6) * (10**(7.5*T/(237.5+T))) / ((237.3+T)**2)  
    
    def calculate_balance(temperature_leaf=0., temperature_air=0., net_radiation=0., 
                          hc=0., hw=0., esa=0., e=0.):
        """ Calculate the energy balance on the leaf surface.
        
        Returns
        -------
        balance: float
            Energy balance on the leaf surface
        """
        # Leaf emissivity
        E = 0.95
        # Stefan- Boltzmann constant (in W.m-2.degrees Kelvin-4)
        S = 5.6704*10**-8
        # Atmospheric pressure (in mbar)
        P = 1013
        Tm = (temperature_leaf + temperature_air)/2
        s = calculate_slope(Tm)
        return (temperature_leaf - temperature_air - 
               ((net_radiation - E*S*(temperature_air+273)**4)-(0.622/P)*2.*hw*(esa-e)) /
               (4*E*S*(Tm+273)**3 + 2*hc + (0.622/P)*2*hw*s))
    
    def find_temp_leaf(temperature_air=0., net_radiation=0., hc=0., hw=0., esa=0., e=0.):
        """ Run an optimization process on the function 'calculate_balance' to find 'temperature_leaf'
        
        Returns
        -------
        temperature_leaf: float
            Temperature of the surface of the leaf (in degrees celsius)
        """
        from scipy.optimize import fsolve
        return fsolve(calculate_balance, temperature_air, args=(net_radiation, hc, hw, esa, e))
    
    hc = calculate_hc(leaf_geometry, wind_speed, wind_direction);
    hw = calculate_hw(hc);
    esa = calculate_psat(temperature_air);
    e = calculate_p(esa, relative_humidity);
    temperature_leaf = find_temp_leaf(temperature_air, net_radiation, hc, hw, esa, e);
    
    print(temperature_leaf)
    esl = calculate_psat(temperature_leaf);
    P = 1013
    LE = -(0.622/P)*2*hw*(esl-e);

    if LE > 0 or rain_intensity>0:
        return True
    else:
        return False
        
def wind_speed_on_leaf(wind_speed=0., leaf_height=0., canopy_height=0., lai=0., lc=0.2, cd=0.3,
                       is_in_rows = True, row_direction=(1,0,0), wind_direction=(1,0,0), param_reduc=0.5):
                       
    """ Calculate the wind speed on a given leaf according to its height in the canopy.
    
    This very simple model makes the assumption that the canopy is completely homogeneous.
    The particular case of interrows is not treated. Also it does not take into account
    the wind direction.
    
    The equation comes from appendix C in the following article:
    TUZET, A., PERRIER, A. and LEUNING, R. (2003), 
    A coupled model of stomatal conductance, photosynthesis and transpiration.
    Plant, Cell and Environment, 26: 1097-1116. doi: 10.1046/j.1365-3040.2003.01035.x
   
    link : http://onlinelibrary.wiley.com/doi/10.1046/j.1365-3040.2003.01035.x/abstract

    Parameters
    ----------
    wind_speed: float
        Wind speed (in m.s-1)
    leaf_height: float
        Leaf height in the canopy (in m)
    canopy_heigth: float
        Height of the highest leaf (in m)
    lai: float
        Leaf Area Index of the canopy (in m2 of leaf / m2 of ground)
    lc: float
        Canopy mixing length (in m)
    cd: float
        Leaf drag coefficient (dimensionless)
    is_in_rows: True or False
        Indicate if there are rows between plants
    row_direction: tuple(x,y,z)
        Direction of vine rows
    wind_direction: tuple(x,y,z)
        Wind direction   
    param_reduc: float
        Maximal reduction of eta for winds parallels to row direction
        
    Returns
    -------
    wind_speed_on_leaf: float
        Wind speed on the given leaf
    """
    from math import exp
    from openalea.plantgl import all as pgl
    
    eta = canopy_height * ( (cd*lai/canopy_height)/(2*lc**2) )**(1./3)
    
    if is_in_rows:
        angle = degrees(pgl.angle(row_direction, wind_direction))
        reduction = param_reduc * (1-angle/90)
        return wind_speed * exp(max(0., eta-reduction)*((leaf_height/canopy_height)-1))
    else:
        return wind_speed * exp(eta*((leaf_height/canopy_height)-1))
    