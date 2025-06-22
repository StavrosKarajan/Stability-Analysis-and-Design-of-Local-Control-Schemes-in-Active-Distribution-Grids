#!/usr/bin/env bash

# Shell script used as a "Makefile-like" helper tool for automated tests and code style checks
# This script can be run using a standard installation of Git on Windows in the Git-BASH.


for KEYWORD in "$@"
do
    case "${KEYWORD}"
    in

        "lint")
			# automated code style checks with flake8
            flake8 ./
            echo flake8 finished
            ;;

        "test")
            # run python tests
            python -m pytest ./test/
            ;;

        *)
            # default action if no keyword specified
            echo Make inactive, no keyword specified
            ;;
    esac
done
