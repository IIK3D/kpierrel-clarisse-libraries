# This script creates an Image base lighting setup in the current context
#
# Copyright (C) 2009 - 2015 Isotropix SAS. All rights reserved.
#
# The information in this file is provided for the exclusive use of
# the software licensees of Isotropix. Contents of this file may not
# be distributed, copied or duplicated in any form, in whole or in
# part, without the prior written permission of Isotropix SAS.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

extensions = 'All Known Files...\t*.{exr,tif,tx,hdr,tga,png,jpg,jpeg,bmp,sgi,psd,pic}\n\
Open EXR \t*.{exr}\nTIFF \t*.{tif}\nTX \t*.{tx}\n\
HDR \t*.{hdr}\nTarga \t*.{tga}\nPNG \t*.{png}\nJPG \t*.{jpg}\n\
JPEG \t*.{jpeg}\nBMP \t*.{bmp}\nSGI \t*.{sgi}\nPSD \t*.{psd}\n\
PIC \t*.{pic}'
file = ix.api.GuiWidget.open_file(ix.application, '', 'Browse for an image', extensions)
if file != "":
    create_env = 1
    ix.begin_command_batch("IBLSetupCreate")
    tx = ix.cmds.CreateObject('ibl_tx', 'TextureMapFile')
    tx.attrs.projection = 5
    tx.attrs.filename = file
    tx.attrs.interpolation_mode = 1
    tx.attrs.mipmap_filtering_mode = 1
    tx.attrs.color_space_auto_detect = False
    tx.attrs.file_color_space = 'linear'
    tx.attrs.pre_multiplied = False
    light = ix.cmds.CreateObject('ibl', 'LightPhysicalEnvironment')
    ix.cmds.SetTexture([light.get_full_name() + ".color"], tx.get_full_name())
    if create_env:
        env = ix.cmds.CreateObject('ibl_env', 'GeometrySphere')
        env_mat = ix.cmds.CreateObject('ibl_mat', 'MaterialMatte')
        env.attrs.override_material = env_mat
        env.attrs.unseen_by_camera = True
        env.attrs.cast_shadows = False
        env.attrs.receive_shadows = False
        env.attrs.is_emitter = False
        env.attrs.radius = 500000
        env.attrs.unseen_by_rays = True
        env.attrs.unseen_by_reflections = True
        env.attrs.unseen_by_refractions = True
        env.attrs.unseen_by_gi = True
        env.attrs.unseen_by_sss = True
        ix.cmds.SetTexture([env_mat.get_full_name() + ".color"], tx.get_full_name())
        #ix.cmds.SetTexture([light.get_full_name() + ".parent"], env.get_full_name())
        light.attrs.parent =env
    ix.end_command_batch()

else:
    ix.log_warning('Image Based Lighting setup has been aborted.')
