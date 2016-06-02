# Releasing a new version of scikit-bio

## Introduction

This guide explains how to release a new version of scikit-bio. To illustrate examples of commands you might run, let's assume that the current version is 1.2.3-dev and we want to release version 1.2.4. Our versioning system is based on Semantic Versioning, which you can read about at http://semver.org.

**Note:** The following commands assume you are in the top-level directory of the scikit-bio repository unless otherwise noted. They also assume that you have [virtualenv](http://virtualenv.readthedocs.org/en/latest/#)/[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) installed.

**Tip:** It can be efficient to have the help of a couple other devs, as some steps can be run in parallel. It's also useful to have a variety of platforms/environments to test on during the release process, so find friends that are Linux and Mac users!

## Prep the release (part 1)

1. Ensure the Travis build is passing against master.

2. Update the version strings (1.2.3-dev) to the new version (1.2.4). There should only be one place this needs to be done: ``skbio/__init__.py``. It's a good idea to ``grep`` for the current version string just to be safe:

        grep -ir '1\.2\.3-dev' *

3. Update ``CHANGELOG.md`` to include descriptions of the changes that made it into this release. Be sure to update the heading to include the new version (1.2.4) and the date of the release. Use the existing structure in the file as a template/guide.

4. Submit a pull request with these changes and let Travis run.

## Build the documentation

In the meantime, you can build the documentation and update the website.

**Note:** You will need to **fully install** (including built extensions) the exact version of scikit-bio that you are editing so that Sphinx will pull docstrings from the correct version of the code. **Make sure the version of scikit-bio that is imported by ``import skbio`` is the correct one!**

1. Build the documentation locally:

        make -C doc clean html

2. Switch to the ``gh-pages`` branch of the repository.

3. Remove everything from ``docs/latest/``:

        git rm -rf docs/latest/*

4. Create a directory for the new version of the docs and recreate the ``latest/`` directory:

        mkdir docs/1.2.4
        mkdir docs/latest

5. Copy over the built documentation to both ``docs/1.2.4/`` and ``docs/latest``:

        cp -r <path to skbio repo>/doc/build/html/* docs/1.2.4/
        cp -r <path to skbio repo>/doc/build/html/* docs/latest/

6. Add a new list item to ``index.html`` to link to ``docs/1.2.4/index.html``.

7. Test out your changes by opening the site locally in a browser. Be sure to check the error console for any errors.

8. Commit and push (either directly or as a pull request) to have the website updated. **Note:** This updates the live website, so be sure to poke through the live site to make sure things aren't broken and that version strings are correct.

## Prep the release (part 2)

If the tests passed on Travis (see step 4 of **Prep the release (part 1)** above), merge the pull request to update the version strings to 1.2.4.

## Tag the release

From the [scikit-bio GitHub page](https://github.com/biocore/scikit-bio), click on the releases tab and draft a new release. Use the version number for the tag name (1.2.4) and create the tag against master. Fill in a release title that is consistent with previous release titles and add a summary of the release (linking to ``CHANGELOG.md`` is a good idea). This release summary will be the primary information that we point users to when we announce the release.

Once the release is created on GitHub, it's a good idea to test out the release tarball before publishing to PyPI:

1. Create a new virtualenv.

2. Download the release tarball from GitHub, extract it, and ``cd`` into the top-level directory.

3. Install the release and run the tests:

        pip install .
        cd
        python -m skbio.test

4. During this process (it can take awhile to install all of scikit-bio's dependencies), submit a pull request to update the version strings from 1.2.4 to 1.2.4-dev. Use the same strategy described above to update the version strings. Update ``CHANGELOG.md`` to include a new section for 1.2.4-dev (there won't be any changes to note here yet). **Do not merge this pull request yet.**

## Test the source distribution

Assuming the GitHub release tarball correctly installs and passes its tests, you're now ready to test the creation of the source distribution (``sdist``) that will be published to PyPI. It is important to test the source distribution because it is created in an entirely different way than the release tarball on GitHub. Thus, there is the danger of having two different release tarballs: the one created on GitHub and the one uploaded to PyPI.

1. Download the release tarball from GitHub, extract it, and ``cd`` into the top-level directory.

2. Build a source distribution:

        python setup.py build_ext --inplace sdist

3. Create a new virtualenv and run:

        cd
        pip install <path to extracted scikit-bio release>/dist/scikit-bio-1.2.4.tar.gz
        python -m skbio.test

4. If everything goes well, it is finally time to push the release to PyPI:

        python setup.py sdist upload

    You must have the proper login credentials to add a release to PyPI. Currently [@gregcaporaso](https://github.com/gregcaporaso) has these, but they can be shared with other release managers.

5. Once the release is available on PyPI, do a final round of testing. Create a new virtualenv and run:

        cd
        pip install scikit-bio
        python -m skbio.test

    If this succeeds, the pypi release appears to be a success.

6. Next, we'll prepare and post the release to [anaconda.org](http://www.anaconda.org).

    You'll need to have ``conda-build`` and ``anaconda-client`` installed to perform these steps. Both can be conda-installed. First, log into anaconda with your anaconda username using the following command. You should have access to push to the ``biocore`` anaconda account through your account (if you don't, get in touch with [@gregcaporaso](https://github.com/gregcaporaso) who is the owner of that account).

        anaconda login

    Due to its C extensions, releasing scikit-bio packages for different platforms will require you to perform the following steps on each of those platforms. For example, an ``osx-64`` package will need to be built on OS X, and a ``linux-64`` package will need to be built on 64-bit Linux. These steps will be the same on all platforms, so you should repeat them for every platform you want to release for.

        conda skeleton pypi scikit-bio
        conda build scikit-bio --python 3.4
        conda build scikit-bio --python 3.5

    At this stage you have built Python 3.4 and 3.5 packages. The absolute path to the packages will be provided as output from each ``conda build`` commands. You should now create conda environments for each, and run the tests as described above. You can install these local packages as follows:

        conda install --use-local scikit-bio

    If the tests pass, you're ready to upload.

        anaconda upload -u biocore <package-filepath>

    ``<package-filepath>`` should be replaced with the path to the package that was was created above. Repeat this for each package you created (here, the Python 3.4 and 3.5 packages).

    After uploading, you should create new environments for every package you uploaded, install scikit-bio from each package, and re-run the tests. You can install the packages you uploaded as follows:

        conda install -c https://conda.anaconda.org/biocore scikit-bio

## Post-release cleanup

1. Merge the latest pull request to update version strings to 1.2.4-dev.

2. Close the release milestone on the GitHub issue tracker.

3. Send an email to the skbio users and developers lists, and anyone else who might be interested (e.g., lab mailing lists). You might include links to the GitHub release page and ``CHANGELOG.md``.

4. Tweet about the release, including a link to the GitHub release page (for example, for 0.1.3, the URL to include was https://github.com/biocore/scikit-bio/releases/tag/0.1.3).

5. :beers:
