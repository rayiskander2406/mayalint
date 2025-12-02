name = "mayaLint"


@early()
def version():
    import sys, os

    sys.path.append(os.getcwd())

    import mayaLint

    return mayaLint.__version__


help = "https://jakejk.io/mayaLint"

description = " Sanity checking tool for polygon models in Maya"

authors = ["Jakob Kousholt", "Niels Peter Kaagaard "]

variants = [["python-2.7"], ["python-3+<4"]]


def commands():
    env.PYTHONPATH.append("{root}/python")
