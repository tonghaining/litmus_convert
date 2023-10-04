#!/usr/bin/env python3

import os

from parser import *
from ptx_output import *
from vulkan_output import *


def parse_file(path, test_name, link, arch):
    file = open(path, mode='r')
    test_text = file.read()
    file.close()
    output = ""
    try:
        test = parse(test_text)
    except Exception as e:
        print(f"Error parsing {path}: {test_name}")
        raise Exception(f"Error parsing {path}: {e}")
    program = test.to_program()
    if arch == "ptx":
        output = PTXOutput(test_name, program, link)
    elif arch == "vulkan":
        output = VulkanOutput(test_name, program, link)
    res = output.dat3m_print()
    return res


def write_file(path, test_name, parse_res):
    file = open(path + f"/{test_name}.litmus", mode='w')
    file.write(parse_res)
    file.close()


def iterate_input_files(in_path, ptx_path, vulkan_path):
    tests = []
    for folder in os.listdir(in_path):
        for sub_folder in os.listdir(os.path.join(in_path, folder)):
            if sub_folder != "alloy_output":
                continue
            for sub_sub_folder in os.listdir(os.path.join(in_path, folder, sub_folder)):
                for file in os.listdir(os.path.join(in_path, folder, sub_folder, sub_sub_folder)):
                    if file.endswith("_simple.txt"):
                        test_name = file.strip(".txt")
                        print(f"Processing {folder}/{test_name}")
                        test_input_path = os.path.join(in_path, folder, sub_folder, sub_sub_folder, file)
                        ptx_parsed = parse_file(test_input_path, test_name, (folder, sub_sub_folder), "ptx")
                        vulkan_parsed = parse_file(test_input_path, test_name, (folder, sub_sub_folder), "vulkan")
                        write_file(os.path.join(ptx_path, folder), test_name, ptx_parsed)
                        write_file(os.path.join(vulkan_path, folder), test_name, vulkan_parsed)
                        tests.append(f"{folder}/{test_name}")
    return tests


def prepare_expectation(tests, expectation_path):
    prefix_vulkan = "litmus/VULKAN/Cadp/"
    prefix_ptx = "litmus/PTX/Cadp/"
    sufix = ".litmus,1"
    with open(f"{expectation_path}_ptx.csv", mode='w') as file:
        for test in tests:
            file.write(prefix_ptx + test + sufix + "\n")
    with open(f"{expectation_path}_vulkan.csv", mode='w') as file:
        for test in tests:
            file.write(prefix_vulkan + test + sufix + "\n")


def main():
    file_path = os.path.dirname(os.path.realpath(__file__))

    input_path = os.path.join(file_path, "cadp_input")
    ptx_path = os.path.join(file_path, "ptx_output")
    vulkan_path = os.path.join(file_path, "vulkan_output")

    tests = iterate_input_files(input_path, ptx_path, vulkan_path)
    prepare_expectation(tests, os.path.join(file_path, "expectation"))


if __name__ == "__main__":
    main()