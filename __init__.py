# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flaechensumme
                                 A QGIS plugin
 Berechnet Flaechensummen
                             -------------------
        begin                : 2015-09-25
        copyright            : (C) 2015 by Max G.
        email                : Lorjax@gmx.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Flaechensumme class from file Flaechensumme.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .flaechen_summe import Flaechensumme
    return Flaechensumme(iface)
