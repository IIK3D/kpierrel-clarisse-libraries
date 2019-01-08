################################################################
# import_speedtree.py
#
# *** INTERACTIVE DATA VISUALIZATION (IDV) PROPRIETARY INFORMATION ***
#
# This software is supplied under the terms of a license agreement or
# nondisclosure agreement with Interactive Data Visualization and may
# not be copied or disclosed except in accordance with the terms of
# that agreement.
#
# Copyright (c) 2003-2017 IDV, Inc.
# All Rights Reserved.
# IDV, Inc.
# Web: http://www.speedtree.com

import os.path as path
import xml.dom.minidom as xmldom
import sys

ix.enable_command_history()

app = ix.application

################################################################
# class SpeedTreeMaterial

class SpeedTreeMap:
    def __init__(self, red = 1.0, green = 1.0, blue = 1.0, file = ""):
        self.red = red
        self.green = green
        self.blue = blue
        self.file = file

class SpeedTreeMaterial:
    def __init__(self, name, twoSided = False, vertexOpacity = False, userData = ""):
        self.clarisse_mat = None
        self.opacity_map = None
        self.name = name.encode('utf-8')
        self.twoSided = twoSided
        self.vertexOpacity = vertexOpacity
        self.userData = userData
        self.maps = { }

def MakeMaterial(context, material):
    new_material = context.add_object(material.name, "MaterialPhysicalStandard")
    result = [new_material, None]

    if (material.maps.has_key("Color")):
        st_map = material.maps["Color"]
        if not st_map.file:
            new_material.attrs.diffuse_front_color[0] = st_map.red
            new_material.attrs.diffuse_front_color[1] = st_map.green
            new_material.attrs.diffuse_front_color[2] = st_map.blue
            if (material.twoSided == True):
                new_material.attrs.diffuse_back_color[0] = st_map.red
                new_material.attrs.diffuse_back_color[1] = st_map.green
                new_material.attrs.diffuse_back_color[2] = st_map.blue
                new_material.attrs.diffuse_back_strength = 1.0
        else:
            color_map = context.add_object("color_map", "TextureMapFile")
            color_map.get_attribute("filename").set_string(st_map.file)
            new_material.get_attribute("diffuse_front_color").set_texture(color_map)
            if (material.twoSided == True):
                new_material.get_attribute("diffuse_back_color").set_texture(color_map)
                new_material.attrs.diffuse_back_strength = 1.0

    if (material.vertexOpacity):
        # get the blend and vertex ao values
        extract = context.add_object("blend_ao", "TextureExtractProperty")
        extract.attrs.property_name = "blend_ao"

        # red has the blend, make a color out of it
        reorder = context.add_object("blend_color", "TextureReorder")
        reorder.attrs.channel_order = "rrr1"
        reorder.get_attribute("input").set_texture(extract)

        multiply = context.add_object("final_opacity", "TextureMultiply")
        multiply.get_attribute("input1").set_texture(reorder)
        if (material.maps.has_key("Opacity")):
            st_map = material.maps["Opacity"]
            if not st_map.file:
                color = context.add_object("opacity_color", "TextureConstantColor")
                color.attrs.color[0] = st_map.red
                color.attrs.color[1] = st_map.green
                color.attrs.color[2] = st_map.blue
                multiply.get_attribute("input2").set_texture(color)
            else:
                opacity_map = context.add_object("opacity_map", "TextureMapFile")
                result[1] = opacity_map
                opacity_map.get_attribute("filename").set_string(st_map.file)
                opacity_map.attrs.single_channel_file_behavior = 1;
                opacity_map.attrs.use_raw_data = 1;
                multiply.get_attribute("input2").set_texture(opacity_map)

        new_material.get_attribute("opacity").set_texture(multiply)
    else:
        if (material.maps.has_key("Opacity")):
            st_map = material.maps["Opacity"]
            if not st_map.file:
                new_material.attrs.opacity[0] = st_map.red
                new_material.attrs.opacity[1] = st_map.green
                new_material.attrs.opacity[2] = st_map.blue
            else:
                opacity_map = context.add_object("opacity_map", "TextureMapFile")
                result[1] = opacity_map
                opacity_map.get_attribute("filename").set_string(st_map.file)
                opacity_map.attrs.single_channel_file_behavior = 1;
                opacity_map.attrs.use_raw_data = 1;
                new_material.get_attribute("opacity").set_texture(opacity_map)

    # flip the tangents on the backside so it will light correctly
    if (material.maps.has_key("Normal")):
        st_map = material.maps["Normal"]
        if st_map.file:
            normal_map = context.add_object("normal_map", "TextureMapFile")
            normal_map.get_attribute("filename").set_string(st_map.file)
            normal_map.get_attribute("single_channel_file_behavior").set_long(1)
            normal_map.attrs.use_raw_data = 1;
            backside_remap = context.add_object("backside_remap", "TextureRemap")
            backside_remap.get_attribute("input").set_texture(normal_map);
            curve = backside_remap.get_attribute("output").get_curve(0)
            curve.get_key_at(0).set_value(1)
            curve.get_key_at(1).set_value(0)
            curve = backside_remap.get_attribute("output").get_curve(1)
            curve.get_key_at(0).set_value(1)
            curve.get_key_at(1).set_value(0)
            backside_switch = context.add_object("backside_switch", "TextureSideSwitch")
            backside_switch.get_attribute("front_color").set_texture(normal_map);
            backside_switch.get_attribute("back_color").set_texture(backside_remap);
            normal = context.add_object("normal", "TextureNormalMap")
            normal.get_attribute("input").set_texture(backside_switch)
            new_material.get_attribute("normal_input").set_texture(normal)

    if (material.maps.has_key("Gloss")):
        st_map = material.maps["Gloss"]
        if not st_map.file:
            new_material.attrs.diffuse_roughness = 1.0 - st_map.red
            new_material.attrs.specular_1_roughness = 1.0 - st_map.red
        else:
            gloss_map = context.add_object("gloss_map", "TextureMapFile")
            gloss_map.get_attribute("filename").set_string(st_map.file)
            gloss_map.attrs.single_channel_file_behavior = 1
            gloss_map.attrs.invert = 1
            gloss_map.attrs.use_raw_data = 1;

            new_material.get_attribute("diffuse_roughness").set_texture(gloss_map)
            new_material.get_attribute("specular_1_roughness").set_texture(gloss_map)

    # fix for IOR on backside normal map
    ior_switch = context.add_object("ior", "TextureSideSwitch")
    ior_switch.attrs.front_color[0] = 1.4
    ior_switch.attrs.front_color[1] = 1.4
    ior_switch.attrs.front_color[2] = 1.4
    ior_switch.attrs.back_color[0] = 0.7
    ior_switch.attrs.back_color[1] = 0.7
    ior_switch.attrs.back_color[2] = 0.7
    new_material.get_attribute("specular_1_index_of_refraction").set_texture(ior_switch)

    if (material.maps.has_key("Specular")):
        st_map = material.maps["Specular"]
        if not st_map.file:
            new_material.attrs.specular_1_color[0] = st_map.red
            new_material.attrs.specular_1_color[1] = st_map.green
            new_material.attrs.specular_1_color[2] = st_map.blue
        else:
            specular_map = context.add_object("specular_map", "TextureMapFile")
            specular_map.get_attribute("filename").set_string(st_map.file)
            specular_map.attrs.use_raw_data = 1;

            new_material.get_attribute("specular_1_color").set_texture(specular_map)


    if (material.maps.has_key("SubsurfaceAmount")):
        st_map = material.maps["SubsurfaceAmount"]
        if not st_map.file:
            new_material.attrs.diffuse_back_strength = st_map.red
        else:
            transmission_amount_map = context.add_object("transmission_amount_map", "TextureMapFile")
            transmission_amount_map.get_attribute("filename").set_string(st_map.file)
            transmission_amount_map.attrs.single_channel_file_behavior = 1
            transmission_amount_map.attrs.use_raw_data = 1;
            new_material.get_attribute("diffuse_back_strength").set_texture(transmission_amount_map)

    if (material.maps.has_key("SubsurfaceColor")):
        st_map = material.maps["SubsurfaceColor"]
        if not st_map.file:
            new_material.attrs.diffuse_back_color[0] = st_map.red
            new_material.attrs.diffuse_back_color[1] = st_map.green
            new_material.attrs.diffuse_back_color[2] = st_map.blue
        else:
            transmission_color_map = context.add_object("transmission_color_map", "TextureMapFile")
            transmission_color_map.get_attribute("filename").set_string(st_map.file)
            new_material.get_attribute("diffuse_back_color").set_texture(transmission_color_map)

    return result


def ProcessContext(context, aMaterials):

    for i in aMaterials:
        material = aMaterials[i]

        try:
            mat_context = context.add_context("st_" + material.name)
            result = MakeMaterial(mat_context, material)
            material.clarisse_mat = result[0]
            material.opacity_map = result[1]

        except:
            print "SpeedTree ERROR: Failed to create material '" + material.name + "'."
            print sys.exc_info()

    abc_objects = ix.api.OfObjectArray( )
    context.get_objects("GeometryAbcMesh", abc_objects);

    for object in abc_objects:
        object.attrs.smoothing_mode = 0
        for index in range (0, len(object.attrs.shading_groups)):
            for i in aMaterials:
                material = aMaterials[i]
                if (object.attrs.shading_groups[index] == material.name + "SG"):
                    object.get_module( ).assign_material(material.clarisse_mat.get_module( ), index)
                    if (material.opacity_map != None):
                        object.get_module( ).assign_clip_map(material.opacity_map.get_module( ), index)
                    break;

    poly_objects = ix.api.OfObjectArray( )
    context.get_objects("GeometryPolyfile", poly_objects);

    for object in poly_objects:
        object.attrs.smoothing_mode = -1
        for index in range (0, len(object.attrs.shading_groups)):
            for i in aMaterials:
                material = aMaterials[i]
                if (object.attrs.shading_groups[index] == material.name):
                    object.get_module( ).assign_material(material.clarisse_mat.get_module( ), index)
                    break;

    old_materials = ix.api.OfObjectArray( )
    context.get_objects("MaterialStandard", old_materials)
    for old_material in old_materials:
        context.remove_object(old_material)

    old_maps = ix.api.OfObjectArray( )
    context.get_objects("TextureMapFile", old_maps)
    for old_map in old_maps:
        context.remove_object(old_map)

title = "Import SpeedTree Files..."
filter = "SpeedTree material files\t*.{stmat}"
filenames = ix.api.GuiWidget.open_files(app, app.get_current_project_filename(), title, filter)

clarisse_win = app.get_event_window()
clarisse_win.set_mouse_cursor(ix.api.Gui.MOUSE_CURSOR_WAIT)


for i in range (filenames.get_count()):
    stmatFilename = path.splitext(filenames[i])[0] + ".stmat"
    stmatDir = path.dirname(path.abspath(stmatFilename)) + "\\"
    meshFile = ""
    aNewMaterials = { }

    try:
        xmlDoc = xmldom.parse(stmatFilename)
        xmlRoot = xmlDoc.getElementsByTagName('Materials')
        if len(xmlRoot) > 0:
            #parse mesh info
            meshFile = (stmatDir + xmlRoot[0].attributes["Mesh"].value).encode('utf-8')

            # load speedtree materials
            materials = xmlRoot[0].getElementsByTagName('Material')
            for material in materials:
                stMaterial = SpeedTreeMaterial(material.attributes["Name"].value,
                                                material.attributes["TwoSided"].value == "1",
                                                material.attributes["VertexOpacity"].value == "1",
                                                material.attributes["UserData"].value)
                maps = material.getElementsByTagName('Map')
                for stmap in maps:
                    newmap = SpeedTreeMap()
                    if (stmap.attributes.has_key("File")):
                        newmap.file = (stmatDir + stmap.attributes["File"].value).encode('utf-8')
                    elif (stmap.attributes.has_key("Value")):
                        newmap.red = newmap.green = newmap.blue = float(stmap.attributes["Value"].value)
                    else:
                        newmap.red = float(stmap.attributes["ColorR"].value)
                        newmap.green = float(stmap.attributes["ColorG"].value)
                        newmap.blue = float(stmap.attributes["ColorB"].value)

                    stMaterial.maps[stmap.attributes["Name"].value] = newmap
                    aNewMaterials[stMaterial.name] = stMaterial

        if (meshFile):
            extension = path.splitext(meshFile)[1]

            # OBJ options
            if (extension == ".obj"):
                try:
                    current = ix.application.get_current_context( )
                    geo_name = path.splitext(path.basename(meshFile))[0]
                    new_context = current.add_context(geo_name)
                    ix.api.IOHelpers.import_geometry(new_context, meshFile, 1)
                    ProcessContext(new_context, aNewMaterials)
                except:
                    print "LOAD ERROR: could not load " + meshFile
                    print sys.exc_info()

            # alembic options
            if (extension == ".abc"):
                try:
                    context = ix.import_scene(meshFile)
                    ProcessContext(context, aNewMaterials)
                except:
                    print "LOAD ERROR: could not load " + meshFile
                    print sys.exc_info()

    except:
        print "SpeedTree ERROR: Failed to read SpeedTree stmat file"

clarisse_win.set_mouse_cursor(ix.api.Gui.MOUSE_CURSOR_DEFAULT)
ix.disable_command_history()

