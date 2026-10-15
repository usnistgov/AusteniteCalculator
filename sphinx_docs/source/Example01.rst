Example 05 - Withdrawn NIST SRM
================================

=========================
Background
=========================

The National Institute of Standards and Technology (NIST, formerly the National Bureau of Standards or NBS) develops Standard Reference Materials (SRMs) and Reference Materials (RMs) for the support of accurate and compatible measurements.
The SRM 487 series were developed to nominally have 30% retained austenite mixed with 70% martensite.  These phase fractions were measured with x-ray flourescence and optical microscopy; but were not measured with x-ray diffraction.  Subsequent disagreement between the x-ray diffraction measurement and the certified values lead to the SRM 487 series being withdrawn as an SRM. More information is available at https://doi.org/10.6028/NBS.SP.260-78

While SRM 487 is no longer approved as an SRM, it remains a well documented and characterized sample, and was used an an example material.




310 Stainless Steel, composition from NBS SP 260-78. Lattice parameters fit from datafile. Source for Uiso?

Low/high 310 Stainless Steel, composition from https://www.theworldmaterial.com/aisi-310-stainless-steel/. Lattice parameters fit from datafile.
430 Stainless Steel, composition from NBS SP 260-78. Lattice parameters fit from datafile.

Low/High 430 Stainless Steel, composition from https://www.theworldmaterial.com/astm-aisi-430-grade-stainless-steel/. Lattice parameters fit from datafile.

Source for Uiso?

 NIST MML Bruker D8 Used process from part 1 of https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm and E211110-AAC-001_005-000_exported.csv as the data set.

=========================
Usage
=========================


=========================
Expected Output
=========================
.. list output with version number


=========================
File Description Table
=========================
.. Check we're using the same wording as the app
.. VERY rigid structure.  "|" and  "+" must all be in the same column position for ALL rows

+---------+-------------------------------------+-----------------+----------------+--------+-------------+
|    Type |                            Filename |         Data ID |    Acquired by | Format | Description |
+=========+=====================================+=================+================+========+=============+
|DataFile | E211110-AAC-001_019-000_exported.csv| E211110-AAC-001 | Adam Creuziger |    csv | SRM 487-157 |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|                austenite-SRM487.cif | n/a             | Adam Creuziger | cif    |310 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|           austenite-SRM487-high.cif | n/a             | Caleb Schenck  | cif    |310 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|            austenite-SRM487-low.cif | n/a             | Caleb Schenck  | cif    |310 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|                  ferrite-SRM487.cif | n/a             | Adam Creuziger | cif    |430 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|             ferrite-SRM487-high.cif | n/a             | Caleb Schenck  | cif    |430 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
| CIF File|              ferrite-SRM487-low.cif | n/a             | Caleb Schenck  | cif    |430 SS       |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+
|InstParam|            BrukerD8_E211110.instprm | n/a             | Adam Creuziger | instprm|Bruker D8    |
+---------+-------------------------------------+-----------------+----------------+--------+-------------+





.. automodule:: user_guide
    :members:
