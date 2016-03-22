#!/bin/bash

thisdir=`pwd`

# --- SET UP ENVIRONMENT VARIABLES ---
echo --- setting up environment variables ---
# presumed location of MATLAB Compiler Runtime (MCR) v7.14
# if the MCR is in a different location, edit the line below
mcr_root="$thisdir/MATLAB_Compiler_Runtime"
export LD_LIBRARY_PATH=$mcr_root/v714/runtime/glnxa64:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$mcr_root/v714/sys/os/glnxa64:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$mcr_root/v714/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$mcr_root/v714/sys/java/jre/glnxa64/jre/lib/amd64/server:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$mcr_root/v714/sys/java/jre/glnxa64/jre/lib/amd64:$LD_LIBRARY_PATH
export XAPPLRESDIR=$mcr_root/v714/X11/app-defaults
# (these may be set permanently by copying the above lines into your login script)


./gp_gistic2_from_seg

