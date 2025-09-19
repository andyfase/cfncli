# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andyfase/cfncli/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                            |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| cfncli/\_\_init\_\_.py                                          |        5 |        2 |     60% |       7-8 |
| cfncli/\_\_main\_\_.py                                          |        7 |        7 |      0% |      3-15 |
| cfncli/cli/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| cfncli/cli/autocomplete.py                                      |       16 |        0 |    100% |           |
| cfncli/cli/commands/\_\_init\_\_.py                             |        0 |        0 |    100% |           |
| cfncli/cli/commands/drift/\_\_init\_\_.py                       |        1 |        1 |      0% |         1 |
| cfncli/cli/commands/drift/detect/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| cfncli/cli/commands/drift/detect/detect.py                      |       14 |       14 |      0% |      3-23 |
| cfncli/cli/commands/drift/diff/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| cfncli/cli/commands/drift/diff/diff.py                          |       12 |       12 |      0% |      3-21 |
| cfncli/cli/commands/drift/drift.py                              |        9 |        9 |      0% |      1-15 |
| cfncli/cli/commands/generate/\_\_init\_\_.py                    |        1 |        0 |    100% |           |
| cfncli/cli/commands/generate/generate.py                        |       16 |        1 |     94% |        29 |
| cfncli/cli/commands/stack/\_\_init\_\_.py                       |        1 |        0 |    100% |           |
| cfncli/cli/commands/stack/cancel/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/cancel/cancel.py                      |       23 |       14 |     39% |     18-37 |
| cfncli/cli/commands/stack/changeset/\_\_init\_\_.py             |        1 |        0 |    100% |           |
| cfncli/cli/commands/stack/changeset/changeset.py                |        9 |        0 |    100% |           |
| cfncli/cli/commands/stack/changeset/create/\_\_init\_\_.py      |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/changeset/create/create.py            |       36 |        3 |     92% | 45, 47-48 |
| cfncli/cli/commands/stack/changeset/exec/\_\_init\_\_.py        |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/changeset/exec/exec.py                |       25 |        0 |    100% |           |
| cfncli/cli/commands/stack/delete/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/delete/delete.py                      |       19 |        2 |     89% |     30-31 |
| cfncli/cli/commands/stack/deploy/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/deploy/deploy.py                      |       18 |        0 |    100% |           |
| cfncli/cli/commands/stack/describe/\_\_init\_\_.py              |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/describe/describe.py                  |       15 |        5 |     67% |     19-31 |
| cfncli/cli/commands/stack/stack.py                              |       21 |        0 |    100% |           |
| cfncli/cli/commands/stack/sync/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/sync/sync.py                          |       20 |        4 |     80% |     56-71 |
| cfncli/cli/commands/stack/tail/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/tail/tail.py                          |       18 |        8 |     56% |     29-42 |
| cfncli/cli/commands/stack/update/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| cfncli/cli/commands/stack/update/update.py                      |       19 |        0 |    100% |           |
| cfncli/cli/commands/status/\_\_init\_\_.py                      |        1 |        0 |    100% |           |
| cfncli/cli/commands/status/status.py                            |       17 |        3 |     82% |     20-22 |
| cfncli/cli/commands/validate/\_\_init\_\_.py                    |        1 |        0 |    100% |           |
| cfncli/cli/commands/validate/validate.py                        |       25 |        3 |     88% |     30-32 |
| cfncli/cli/context.py                                           |       65 |        1 |     98% |        45 |
| cfncli/cli/main.py                                              |       43 |        4 |     91% |33-35, 126 |
| cfncli/cli/multicommand.py                                      |       28 |        9 |     68% |35-37, 41-43, 47-49 |
| cfncli/cli/types.py                                             |       10 |        0 |    100% |           |
| cfncli/cli/utils/\_\_init\_\_.py                                |        0 |        0 |    100% |           |
| cfncli/cli/utils/colormaps.py                                   |       28 |        0 |    100% |           |
| cfncli/cli/utils/common.py                                      |        7 |        1 |     86% |         8 |
| cfncli/cli/utils/deco.py                                        |       29 |        6 |     79% |24, 29-32, 36 |
| cfncli/cli/utils/events.py                                      |       68 |       10 |     85% |95, 102, 113, 129-135, 150-151, 163 |
| cfncli/cli/utils/pager.py                                       |       12 |       11 |      8% |      8-23 |
| cfncli/cli/utils/pprint.py                                      |      267 |       67 |     75% |54, 91, 94, 123-125, 130-139, 154, 156, 164-168, 173-190, 209, 211-213, 216-225, 375, 378-385, 411-415, 425-434 |
| cfncli/config/\_\_init\_\_.py                                   |       23 |        5 |     78% |     29-33 |
| cfncli/config/config.py                                         |       28 |        1 |     96% |        27 |
| cfncli/config/deployment.py                                     |       63 |        6 |     90% |48-50, 98-99, 102 |
| cfncli/config/formats.py                                        |      117 |       30 |     74% |29-34, 41, 44, 51, 54-55, 58, 93-97, 109, 126, 147, 151-157, 164, 169-172, 185-186 |
| cfncli/config/schema.py                                         |        8 |        0 |    100% |           |
| cfncli/config/template.py                                       |       16 |        2 |     88% |     30-31 |
| cfncli/ext\_customizations/\_\_init\_\_.py                      |        0 |        0 |    100% |           |
| cfncli/ext\_customizations/cloudformation/\_\_init\_\_.py       |        0 |        0 |    100% |           |
| cfncli/ext\_customizations/cloudformation/artifact\_exporter.py |      313 |       26 |     92% |56, 91, 127, 134-135, 144-147, 227, 232, 235-236, 248-250, 262-263, 451, 455, 536, 541, 548, 576, 624-625, 640 |
| cfncli/ext\_customizations/cloudformation/exceptions.py         |       22 |        3 |     86% |       5-7 |
| cfncli/ext\_customizations/cloudformation/yamlhelper.py         |       40 |        3 |     92% |     49-55 |
| cfncli/ext\_customizations/s3uploader/\_\_init\_\_.py           |        0 |        0 |    100% |           |
| cfncli/ext\_customizations/s3uploader/s3uploader.py             |      103 |       15 |     85% |33-35, 55-57, 95-96, 99, 109-113, 185 |
| cfncli/runner/\_\_init\_\_.py                                   |        2 |        0 |    100% |           |
| cfncli/runner/commands/\_\_init\_\_.py                          |        0 |        0 |    100% |           |
| cfncli/runner/commands/command.py                               |        9 |        1 |     89% |        13 |
| cfncli/runner/commands/drift\_detect\_command.py                |       28 |       28 |      0% |      1-84 |
| cfncli/runner/commands/drift\_diff\_command.py                  |       18 |       18 |      0% |      1-34 |
| cfncli/runner/commands/stack\_changeset\_command.py             |       72 |       15 |     79% |42-44, 92, 95, 102-121, 125 |
| cfncli/runner/commands/stack\_delete\_command.py                |       29 |        2 |     93% |    40, 44 |
| cfncli/runner/commands/stack\_deploy\_command.py                |       35 |        1 |     97% |        55 |
| cfncli/runner/commands/stack\_exec\_changeset\_command.py       |       55 |       15 |     73% |44-47, 60-68, 74, 80, 89, 116 |
| cfncli/runner/commands/stack\_status\_command.py                |       35 |        5 |     86% |28, 46, 54-56 |
| cfncli/runner/commands/stack\_sync\_command.py                  |       29 |       14 |     52% |     37-66 |
| cfncli/runner/commands/stack\_update\_command.py                |       41 |        9 |     78% |50, 56-59, 70-75, 81 |
| cfncli/runner/commands/utils.py                                 |       78 |       25 |     68% |18-25, 37, 44-49, 61, 68-73, 103, 108, 113, 119, 125, 137, 139, 142 |
| cfncli/runner/runbook/\_\_init\_\_.py                           |        2 |        0 |    100% |           |
| cfncli/runner/runbook/base.py                                   |       35 |        5 |     86% |11, 15, 19, 23, 35 |
| cfncli/runner/runbook/boto3\_context.py                         |       53 |        2 |     96% |    72, 87 |
| cfncli/runner/runbook/boto3\_outputs.py                         |       35 |       25 |     29% |     14-53 |
| cfncli/runner/runbook/boto3\_params.py                          |       52 |       15 |     71% |11, 13, 24, 27, 43-56, 71, 81 |
| cfncli/runner/runbook/boto3\_profile.py                         |       22 |        3 |     86% |19, 21, 36 |
| cfncli/runner/runbook/boto3\_runbook.py                         |       47 |        5 |     89% |     24-28 |
| cfncli/runner/runbook/package.py                                |       90 |       35 |     61% |27, 33, 43, 56, 59, 79, 102-117, 127, 130-147, 157-163, 182 |
| cfncli/runner/stack\_selector.py                                |       17 |        5 |     71% | 20-25, 30 |
|                                                       **TOTAL** | **2424** |  **516** | **79%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/andyfase/cfncli/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andyfase/cfncli/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andyfase/cfncli/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/andyfase/cfncli/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fandyfase%2Fcfncli%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/andyfase/cfncli/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.