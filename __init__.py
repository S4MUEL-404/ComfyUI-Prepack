from .py.modelDualCLIP import PrepackModelDualCLIP
from .py.modelSingleCLIP import PrepackModelSingleCLIP
from .py.loras import PrepackLoras
from .py.lorasmssd3 import PrepackLorasAndMSSD3
from .py.ksampler import PrepackKsampler
from .py.ksamplerAdvanced import PrepackKsamplerAdvanced
from .py.setpipe import PrepackSetPipe
from .py.getpipe import PrepackGetPipe
from .py.seed import PrepackSeed
from .py.logicInt import PrepackLogicInt
from .py.logicString import PrepackLogicString
from .py.intCombine import PrepackIntCombine
from .py.intSplit import PrepackIntSplit
from .py.saveByFileName import PrepackSaveByFileName

# Frontend extension directory for virtual nodes
WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "PrepackModelDualCLIP": PrepackModelDualCLIP,
    "PrepackModelSingleCLIP": PrepackModelSingleCLIP,
    "PrepackLoras": PrepackLoras,
    "PrepackLorasAndMSSD3": PrepackLorasAndMSSD3,
    "PrepackKsampler": PrepackKsampler,
    "PrepackKsamplerAdvanced": PrepackKsamplerAdvanced,
    "PrepackSetPipe": PrepackSetPipe,
    "PrepackGetPipe": PrepackGetPipe,
    "PrepackSeed": PrepackSeed,
    "💀Prepack Logic Int": PrepackLogicInt,
    "💀Prepack Logic String": PrepackLogicString,
    "💀Prepack Int Combine": PrepackIntCombine,
    "💀Prepack Int Split": PrepackIntSplit,
    "💀Prepack Save By File Name": PrepackSaveByFileName,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PrepackModelDualCLIP": "💀Prepack Model DualCLIP",
    "PrepackModelSingleCLIP": "💀Prepack Model SingleCLIP",
    "PrepackLoras": "💀Prepack Loras",
    "PrepackLorasAndMSSD3": "💀Prepack Loras and MSSD3",
    "PrepackKsampler": "💀Prepack Ksampler",
    "PrepackKsamplerAdvanced": "💀Prepack Ksampler Advanced",
    "PrepackSetPipe": "💀Prepack SetPipe",
    "PrepackGetPipe": "💀Prepack GetPipe",
    "PrepackSeed": "💀Prepack Seed",
    "💀Prepack Logic Int": "💀Prepack Logic Int",
    "💀Prepack Logic String": "💀Prepack Logic String",
    "💀Prepack Int Combine": "💀Prepack Int Combine",
    "💀Prepack Int Split": "💀Prepack Int Split",
    "💀Prepack Save By File Name": "💀Save By File Name",
}

__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY',
]
