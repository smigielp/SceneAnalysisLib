'''
Created on 5 mar 2017

@author: Mateusz Raczynski
'''

from OpenGL.GL import *

def getShaders():
    shadedShader = loadShader()
    shadedShaderUniforms = createShadedUniformLocations(shadedShader)
    simpleShader = loadShaderExt(__vertexShader_noNormals,__fragmentShader_noNormals)
    simpleShaderUniforms = createSimpleUniformLocations(simpleShader)
    return [[shadedShader,shadedShaderUniforms],[simpleShader,simpleShaderUniforms]]
    #todo: make generic uniform creator

def loadShader():
    VertexShaderID = glCreateShader(GL_VERTEX_SHADER)
    FragmentShaderID = glCreateShader(GL_FRAGMENT_SHADER)

    VertexShaderCode = __vertexShader

    FragmentShaderCode = __fragmentShader

    print ("Compiling shader : %s\n" % "__vertexShader")
    VertexSourcePointer = VertexShaderCode
    glShaderSource(VertexShaderID, VertexSourcePointer)  # , NULL)
    glCompileShader(VertexShaderID)

    Result = glGetShaderiv(VertexShaderID, GL_COMPILE_STATUS)
    InfoLogLength = glGetShaderiv(VertexShaderID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetShaderInfoLog(VertexShaderID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during compiling shaders.")

    print "Compiling shader : %s" % "__fragmentShader"
    FragmentSourcePointer = FragmentShaderCode
    glShaderSource(FragmentShaderID, FragmentSourcePointer)  # , NULL);
    glCompileShader(FragmentShaderID)

    Result = glGetShaderiv(FragmentShaderID, GL_COMPILE_STATUS)
    InfoLogLength = glGetShaderiv(FragmentShaderID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetShaderInfoLog(FragmentShaderID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during compiling shaders.")

    print "Linking program"
    ProgramID = glCreateProgram()
    glAttachShader(ProgramID, VertexShaderID)
    glAttachShader(ProgramID, FragmentShaderID)
    glLinkProgram(ProgramID)

    Result = glGetProgramiv(ProgramID, GL_LINK_STATUS)
    InfoLogLength = glGetProgramiv(ProgramID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetProgramInfoLog(ProgramID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during linking shaders.")

    glDetachShader(ProgramID, VertexShaderID)
    glDetachShader(ProgramID, FragmentShaderID)

    glDeleteShader(VertexShaderID)
    glDeleteShader(FragmentShaderID)

    return ProgramID


def loadShaderExt(vertexShaderCode,fragmentShaderCode):
    VertexShaderID = glCreateShader(GL_VERTEX_SHADER)
    FragmentShaderID = glCreateShader(GL_FRAGMENT_SHADER)

    VertexShaderCode = vertexShaderCode

    FragmentShaderCode = fragmentShaderCode

    print ("Compiling shader : %s\n" % "__vertexShader")
    VertexSourcePointer = VertexShaderCode
    glShaderSource(VertexShaderID, VertexSourcePointer)  # , NULL)
    glCompileShader(VertexShaderID)

    Result = glGetShaderiv(VertexShaderID, GL_COMPILE_STATUS)
    InfoLogLength = glGetShaderiv(VertexShaderID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetShaderInfoLog(VertexShaderID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during compiling shaders.")

    print "Compiling shader : %s" % "__fragmentShader"
    FragmentSourcePointer = FragmentShaderCode
    glShaderSource(FragmentShaderID, FragmentSourcePointer)  # , NULL);
    glCompileShader(FragmentShaderID)

    Result = glGetShaderiv(FragmentShaderID, GL_COMPILE_STATUS)
    InfoLogLength = glGetShaderiv(FragmentShaderID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetShaderInfoLog(FragmentShaderID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during compiling shaders.")

    print "Linking program"
    ProgramID = glCreateProgram()
    glAttachShader(ProgramID, VertexShaderID)
    glAttachShader(ProgramID, FragmentShaderID)
    glLinkProgram(ProgramID)

    Result = glGetProgramiv(ProgramID, GL_LINK_STATUS)
    InfoLogLength = glGetProgramiv(ProgramID, GL_INFO_LOG_LENGTH)
    if InfoLogLength > 0:
        print "%s\n" % glGetProgramInfoLog(ProgramID)
    else:
        print "[log is empty]"
    if Result == 0:
        raise RuntimeError("Error during linking shaders.")

    glDetachShader(ProgramID, VertexShaderID)
    glDetachShader(ProgramID, FragmentShaderID)

    glDeleteShader(VertexShaderID)
    glDeleteShader(FragmentShaderID)

    return ProgramID


def createShadedUniformLocations(programID):
    uniformNames = ["P", "V", "M", "Color"]
    uniforms = [None] * len(uniformNames)
    i = 0
    for name in uniformNames:
        uniforms[i] = glGetUniformLocation(programID, name)
        i += 1

    return uniforms


def createSimpleUniformLocations(programID):
    uniformNames = ["P", "V", "M", "Color"]
    uniforms = [None] * len(uniformNames)
    i = 0
    for name in uniformNames:
        uniforms[i] = glGetUniformLocation(programID, name)
        i += 1

    return uniforms

__vertexShader = '''
#version 130

in vec3 vertexPosition_modelspace;
in vec3 vertexNormal;

uniform mat4 P;
uniform mat4 V;
uniform mat4 M;

out vec3 fragmentNormal;

void main(){
  vec4 position = vec4( vertexPosition_modelspace.xyz,1.0);
  gl_Position = P*V*M*position;
  fragmentNormal = vertexNormal;
}
'''

__fragmentShader = '''
#version 130

#define directionalLightStrength 0.25f
#define ambientLightStrength 0.6f

in vec3 fragmentNormal;

uniform vec3 Color;

out vec4 _color;

void main(){
  vec3 lightDirection = vec3(0.4f,-0.7f,-0.5f);
  float directionalLight = (1.0f - dot(lightDirection,fragmentNormal))*directionalLightStrength;
  directionalLight = clamp(directionalLight,0.0f,1.0f);
  float light = ambientLightStrength + directionalLight;
  light = clamp(light,0.0f,1.0f);
  _color = vec4(Color * light,1.0f); //vec4(light,light,light,1.0f); //
}
'''

__vertexShader_noNormals = '''
#version 130
in vec3 vertexPosition_modelspace;

uniform mat4 P;
uniform mat4 V;
uniform mat4 M;

void main(){
  vec4 position = vec4( vertexPosition_modelspace.xyz,1.0);
  gl_Position = P*V*M*position;
}
'''

__fragmentShader_noNormals = '''
#version 130

#define directionalLightStrength 0.5f
#define ambientLightStrength 0.5f

in vec3 vertexNormal;

uniform vec3 Color;

out vec4 _color;

void main(){
  float light = ambientLightStrength + directionalLightStrength;
  light = clamp(light,0.0f,1.0f);
  _color = vec4(Color * light,1.0f);
}
'''
