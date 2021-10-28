import os
import subprocess
from aws_cdk import core as cdk
from aws_cdk import aws_lambda
from aws_cdk.core import Tags


class CdkLambdaMyLayersStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        base_function = aws_lambda.Function(
            scope=self,
            id='cdk-lambda-my-layers',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            function_name='cdk-lambda-my-layers',
            description='cdk lambda function with my layers',
            code=aws_lambda.Code.asset('src/lambda/base'),
            # tracing=aws_lambda.Tracing.ACTIVE,
            handler='base_app.handler',
            # environment={},
            layers=[self.create_layer(id, 'base')]
        )

        Tags.of(base_function).add('AppName', 'Base')
        cdk.CfnOutput(
            scope=self,
            id='lambda_function_name',
            value=base_function.function_name
        )
        cdk.CfnOutput(
            scope=self,
            id='lambda_function_arn',
            value=base_function.function_arn
        )

    def create_layer(self, project_name, function_name: str) -> aws_lambda.LayerVersion:
        requirements_txt = f'src/lambda/{function_name}/requirements.txt'
        output_dir = f'layers/{function_name}'
        self.pip_install_with_docker(requirements_txt, output_dir)
        # self.pip_install_without_docker(requirements_txt, output_dir)
        return aws_lambda.LayerVersion(
            scope=self,
            id=f'{project_name}-{function_name}-layers',
            code=aws_lambda.Code.from_asset(output_dir),
            layer_version_name=f'custom-{function_name}'
        )

    @staticmethod
    def packages_cmd(requirements_txt, output_dir):
        _packages = list()
        with open(requirements_txt, 'r') as f:
            for line in f:
                _packages.append(line)
        return ' '.join(_packages).replace('\n', '')

    def pip_install_with_docker(self, requirements_txt, output_dir):
        packages = self.packages_cmd(requirements_txt, output_dir)
        current = os.getcwd()
        command = f'docker run --rm -v {current}/{output_dir}:/var/task ' \
                  f'lambci/lambda:build-python3.8 ' \
                  f'pip3 install {packages} -t python --upgrade'

        with open('output.log', 'a') as output:
            subprocess.check_call(
                command,
                shell=True, stdout=output, stderr=output)
        return

    @staticmethod
    def pip_install_without_docker(requirements_txt, output_dir):
        # This method is how To use it in the cdk pipeline.
        # Don't need to use linux environment for lambda when running with CodeBuild.
        subprocess.check_call(
            f'pip3 install -r {requirements_txt} -t {output_dir}/python --upgrade'.split()
        )
        return
