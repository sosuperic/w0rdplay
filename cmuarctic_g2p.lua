-- Use trained g2p model to convert transcripts 
-- Run from synthesis directory

MODEL_PATH = 'g2p/g2p.t7'
G2IDX_PATH = 'g2p/grapheme_to_idx.t7'
P2IDX_PATH = 'g2p/phoneme_to_idx.t7'
DATA_PATH = 'data/cmuarctic/cmuarctic.data.txt'
OUT_PATH = 'data/cmuarctic/data_with_phonemes.txt'

-- Dependencies from model
require 'nngraph'
require 'rnn'
require 'g2p.MaskRNN'
require 'g2p.ReverseMaskRNN'

require 'csvigo'

require 'g2p.lua_utils'
require 'g2p.g2p_utils'

cmd = torch.CmdLine()
cmd:text()
cmd:text('Example:')
cmd:option('-gpuid', 0, 'ID of gpu to run on')
local opt = cmd:parse(arg)

require 'cunn'
require 'cutorch'
require 'cudnn'
cutorch.setDevice((3 - opt.gpuid) + 1)
cutorch.manualSeed(123)

-- Takes string of graphemes (i.e. a word)
-- Returns tensor of dimension (num_graphemes_in_word x num_graphemes)
local function one_hot_encode_word(word, grapheme_to_idx)
	local x = torch.zeros(#word, size_of_table(grapheme_to_idx))
	local i = 1
	for g in word:gmatch"." do
		-- print(i, grapheme_to_idx[g])
		x[i][grapheme_to_idx[g]] = 1
		i = i + 1
	end
	return x
end


print('Loading model')
local model = torch.load(MODEL_PATH)
local grapheme_to_idx = torch.load(G2IDX_PATH)
local num_graphemes = size_of_table(grapheme_to_idx)
local phoneme_to_idx = torch.load(P2IDX_PATH)
local num_phonemes = size_of_table(phoneme_to_idx)
phoneme_to_idx['-'] = 0
local idx_to_phoneme = invert_table(phoneme_to_idx)


local f = io.open(OUT_PATH, 'w')
local lines = lines_from(DATA_PATH)
for i=1,#lines do
	local transcript = split(lines[i], '"')[2]
	local clean = transcript:gsub('%p', ''):gsub('%d', ''):lower()
	local words = split(clean, ' ')
	local transcript_phonemes = {}
	for i, word in ipairs(words) do
		local x = one_hot_encode_word(word, grapheme_to_idx):cuda()
		local inputs = torch.zeros(1, #word, num_graphemes):cuda()
		inputs[1] = x
		local sizes = torch.Tensor({#word}):cuda()	-- length of each input in minibatch
		local activations = model:forward({inputs, sizes})
		activations = activations:view(-1, 1, num_phonemes+1)		-- seq_length x batch x output_dim
		local phonemes = convert_preds_to_phonemes(activations, sizes, idx_to_phoneme)
		table.insert(transcript_phonemes, table.concat(phonemes[1], ' '))
	end
	transcript_phonemes = table.concat(transcript_phonemes, '; ')
	print(transcript)
	print(clean)
	print(transcript_phonemes)

	f:write(transcript .. '\n')
	f:write(clean .. '\n')
	f:write(transcript_phonemes .. '\n')
end

f:close()