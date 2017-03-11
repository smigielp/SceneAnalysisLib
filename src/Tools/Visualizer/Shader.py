'''
Created on 5 mar 2017

@author: Mateusz Raczynski
'''

from OpenGL.GL import *



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


def createUniformLocations(programID):
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
out vec3 color;
uniform mat4 P;
uniform mat4 V;
uniform mat4 M;
uniform vec3 Color;
void main(){
  vec4 position = vec4( vertexPosition_modelspace.xyz,1.0);
  gl_Position = P*V*M*position;
  color = Color;
}
'''

__fragmentShader = '''
#version 130
in vec3 color;
out vec3 _color;
void main(){
  _color = color;
}
'''
