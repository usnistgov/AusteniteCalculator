compute_results
===============
.. automodule:: compute_results
    :members:

.. note::
    This is the main file for the backend of the app

.. note::
    REFORMAT DOCSTRINGS TO GOOGLE STYLE

.. example code block
.. code-block::

   def find_sin_thetas(phase_lattice_parameter, hkl_list, wavelength):
    """
    #Description
    Calculate the position in two theta for a list of hkls.  Used to mark locations for fitting
    !!! Have only tested cubic crystal symmetry
    
    #Input
    phase_lattice_parameter: lattice parameter
    hkl_list: list of lattice planes (hkl)
    wavelength: dominant wavelength in the diffraction data
    
    #Returns
    List of floating point values with the position of each hkl in 2-theta
    #? Is this in radians or degrees?
    #? Returning theta or two_theta?
    """
    D=[phase_lattice_parameter/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

