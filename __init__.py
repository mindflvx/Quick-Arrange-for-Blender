# QUICK ARRANGE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "Quick Arrange",
    "author": "mindflux",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Toolbar > Quick Arrange",
    "description": "Quickly arrange selected objects in a row",
    "category": "Object",
}

import bpy
from . import quick_arrange

def register():
    quick_arrange.register()
    
def unregister():
    quick_arrange.unregister()

if __name__ == "__main__":
    register()
